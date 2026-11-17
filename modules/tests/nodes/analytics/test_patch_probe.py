"""Patch probe on synthetic tokens: held-out groups, cross-fitted frames, the painted map and its failures."""
import types

import pytest
import torch

from modules.nodes.analytics.patch_probe import LF_PatchProbe
from modules.utils.helpers.torch import patch_probe as helper
from modules.utils.helpers.ui import generated_preview

ROWS, COLS, FEATURES, PREFIX = 4, 4, 12, 5


@pytest.fixture(autouse=True)
def preview_root(monkeypatch, tmp_path):
    monkeypatch.setattr(generated_preview, "get_comfy_dir", lambda _kind: str(tmp_path / "input"))


def _encode(images):
    """A CLIP_VISION_OUTPUT-like object: CLS and registers, then row-major patches, of a 64x64 encode."""
    tokens = torch.stack(images)
    prefix = torch.zeros(tokens.shape[0], PREFIX, FEATURES)
    size = torch.Size([3, ROWS * 16, COLS * 16])
    return types.SimpleNamespace(last_hidden_state=torch.cat([prefix, tokens], 1), image_sizes=[size] * len(images))


def _scene(seed, shift, mask=None):
    """[P, D] tokens of one scene: its own content per seed, label 1 shifted along feature 0 (where mask is set)."""
    generator = torch.Generator().manual_seed(seed)
    tokens = torch.randn(ROWS * COLS, FEATURES, generator=generator)
    tokens[:, 1:4] += torch.randn(3, generator=generator) * 2.0  # the scene's content, shared by its two shots
    lift = torch.ones(ROWS * COLS) if mask is None else mask.flatten().float()
    tokens[:, 0] += shift * lift
    return tokens


def _teaching(groups=("a", "b", "c")):
    images, labels, names = [], [], []
    for seed, group in enumerate(groups):
        images += [_scene(seed, 0.0), _scene(seed, 4.0)]
        labels += ["0", "1"]
        names += [group, group]
    return _encode(images), ",".join(labels), ",".join(names)


def test_patch_probe_schema_is_published_api():
    types_ = LF_PatchProbe.INPUT_TYPES()
    assert list(types_["required"]) == ["teach", "labels", "groups", "frames", "frame_images", "crop", "l2"]
    assert list(types_["optional"]) == ["frame_groups", "frame_masks", "names", "ui_widget"]
    assert types_["required"]["crop"][0] == ["none", "center"]
    assert LF_PatchProbe.RETURN_NAMES == ("report", "painted", "probability")
    assert LF_PatchProbe.RETURN_TYPES == ("JSON", "IMAGE", "MASK")
    assert LF_PatchProbe.OUTPUT_IS_LIST == (False, False, False)


def test_each_held_out_scene_reads_its_shift_and_a_new_frame_is_painted_where_it_has_it(monkeypatch):
    sent = []
    monkeypatch.setattr("modules.nodes.analytics.patch_probe.safe_send_sync",
                        lambda event, payload, node_id: sent.append((event, payload, node_id)))
    teach, labels, groups = _teaching()
    left = torch.zeros(ROWS, COLS, dtype=torch.bool)
    left[:, :2] = True
    frames = _encode([_scene(9, 4.0, left), _scene(0, 4.0)])
    images = torch.full((2, 32, 48, 3), 0.5)
    mask = torch.zeros(1, 32, 48)
    mask[:, :, :24] = 1.0
    response = LF_PatchProbe().on_exec(teach=teach, labels=labels, groups=groups, frames=frames,
                                       frame_images=images, crop="none", l2=0.01, frame_groups=",a",
                                       frame_masks=mask, names="off,on", node_id="7")
    report, painted, probability = response["result"]
    assert report["schema"] == "lf.patch-probe.v1"
    assert report["names"] == ["off", "on"]
    held = report["held_out"]
    assert [fold["group"] for fold in held["folds"]] == ["a", "b", "c"]
    assert held["auc_min"] > 0.95 and held["ordered"] == "3/3"
    new, seen = report["frames"]
    assert new["read_by"] == "all groups" and seen["read_by"] == "without a"
    assert new["fold_range"] is not None and seen["fold_range"] is None
    assert new["fold_range"][0] <= new["fold_range"][1] and seen["mean_logit"] > 1.0
    grid = torch.sigmoid(torch.tensor(new["logits"])).reshape(ROWS, COLS)
    assert grid[:, :2].mean() > 0.75 and grid[:, 2:].mean() < 0.25
    assert new["mask_probability"] > 0.7 and seen["mask_probability"] > 0.9
    assert painted.shape == (2, 32, 48, 3) and probability.shape == (2, 32, 48)
    # orange on the shifted half, blue on the other
    assert painted[0, 16, 4, 0] > painted[0, 16, 4, 2] and painted[0, 16, 44, 2] > painted[0, 16, 44, 0]
    event, payload, node_id = sent[0]
    assert (event, node_id) == ("patchprobe", "7")
    assert response["ui"]["lf_output"] == [payload]
    assert "logits" not in payload["report"]["frames"][0] and "logits" in new
    assert len(payload["dataset"]["nodes"]) == 2


def test_a_center_crop_reads_only_the_middle_square():
    probability, covered = helper.probability_map(torch.full((ROWS * COLS,), 4.0), (ROWS, COLS), (20, 40), "center")
    assert covered[:, :10].sum() == 0 and covered[:, 10:30].min() == 1
    assert torch.allclose(probability[:, :10], torch.tensor(0.5)) and probability[:, 10:30].min() > 0.95


def test_the_auc_counts_ties_as_half():
    scores = torch.tensor([0.1, 0.4, 0.4, 0.9])
    labels = torch.tensor([0.0, 0.0, 1.0, 1.0])
    assert helper.roc_auc(scores, labels) == pytest.approx(0.875)
    assert helper.roc_auc(scores, torch.ones(4)) is None


@pytest.mark.parametrize("change, message", [
    ({"labels": "0,1,0"}, "labels names 3"),
    ({"labels": "0,0,0,0,0,0"}, "both 0 and 1"),
    ({"groups": "a,a,a,a,a,a"}, "at least two"),
    ({"groups": "a,a,b,b,c"}, "one group per teaching image"),
    ({"frame_groups": "z,"}, "not among the teaching groups"),
    ({"names": "on"}, "two words"),
    ({"crop": "fit"}, "crop must be"),
])
def test_patch_probe_fails_loud_on_bad_inputs(change, message):
    teach, labels, groups = _teaching()
    inputs = {"teach": teach, "labels": labels, "groups": groups, "frames": _encode([_scene(9, 0.0), _scene(8, 0.0)]),
              "frame_images": torch.full((2, 8, 8, 3), 0.5), "crop": "none", "l2": 0.01}
    inputs.update(change)
    with pytest.raises(ValueError, match=message):
        LF_PatchProbe().on_exec(**inputs)


def test_holding_out_a_group_must_leave_both_labels_to_teach():
    teach = _encode([_scene(0, 0.0), _scene(1, 3.0), _scene(2, 0.0)])
    with pytest.raises(ValueError, match="one label only"):
        helper.held_out(helper.patch_tokens(teach, "teach")[0], [0, 1, 0], ["a", "b", "c"], 0.01)


def test_frames_must_match_the_teaching_grid():
    teach, labels, groups = _teaching()
    odd = types.SimpleNamespace(last_hidden_state=torch.zeros(1, PREFIX + 9, FEATURES),
                                image_sizes=[torch.Size([3, 48, 48])])
    with pytest.raises(ValueError, match="same model and size"):
        helper.read_patch_probe(teach, labels, groups, odd, torch.zeros(1, 8, 8, 3))


def test_the_probe_learns_inside_comfys_inference_mode():
    # ComfyUI executes nodes under torch.inference_mode(), and the encoder's tokens are inference tensors.
    with torch.inference_mode():
        teach, labels, groups = _teaching()
        frames = _encode([_scene(9, 4.0)])
        report, _, _ = helper.read_patch_probe(teach, labels, groups, frames, torch.full((1, 8, 8, 3), 0.5))
    assert report["frames"][0]["mean_probability"] > 0.75


def test_a_pair_both_read_far_on_is_ordered_by_its_logits():
    """Probabilities saturate where a frame reads far to one side; the order of a pair is its logits'."""
    images = [_scene(0, 0.0), _scene(0, 4.0), _scene(1, 0.0), _scene(1, 4.0), _scene(2, 40.0), _scene(2, 60.0)]
    tokens = helper.patch_tokens(_encode(images), "teach")[0]
    folds, _ = helper.held_out(tokens, [0, 1, 0, 1, 0, 1], ["a", "a", "b", "b", "c", "c"], 0.01)
    far = next(fold for fold in folds if fold["group"] == "c")
    off, on = far["images"]
    assert off["mean_probability"] == on["mean_probability"] and on["mean_logit"] > off["mean_logit"]
    assert far["ordered"] is True


def test_the_fit_says_whether_it_converged():
    images = [_scene(seed, shift) for seed in range(3) for shift in (0.0, 4.0)]
    tokens = helper.patch_tokens(_encode(images), "teach")[0].reshape(-1, FEATURES)
    labels = helper._patch_labels([0, 1] * 3, ROWS * COLS)
    fitted = helper.fit_probe(tokens, labels, 0.01)
    assert fitted["converged"] and 0 < fitted["iterations"] < helper.MAX_ITER
    capped = helper.fit_probe(tokens, labels, 0.01, max_iter=1)
    assert not capped["converged"] and capped["iterations"] == 1
