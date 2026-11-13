"""Single-image intrinsic decomposition through Careaga and Aksoy's pipeline ("Colorful Diffuse Intrinsic Image
Decomposition in the Wild", TOG 2024; github.com/compphoto/Intrinsic).

The pipeline estimates an image's albedo (its surfaces' own colour), its diffuse shading (the light they receive, in
colour) and the residual, what neither explains: specular sheen, emitters and clipped pixels. All three are linear.
Neither the ``intrinsic`` package nor its weights ship with LF Nodes: install the package, and put a release's five
stage files (``stage_0*.pt`` .. ``stage_4*.pt``) in one folder under ``models/intrinsic``. The authors provide the code
and models for academic use only.
"""
from __future__ import annotations

import builtins
import contextlib
import logging
import os
import re

import numpy as np
import torch

LOG = logging.getLogger(__name__)
SCHEMA = 'lf.intrinsic-layers.v1'
_STAGE = re.compile(r'^stage_([0-4])(?:_(v\w+))?\.pt$')
_CACHE: dict = {}


def intrinsic_roots() -> list[str]:
    try:
        import folder_paths

        return [os.path.join(folder_paths.models_dir, 'intrinsic')]
    except ImportError:  # outside ComfyUI (tests)
        return []


def available_releases(roots=None) -> list[str]:
    """Release names found under the roots: a folder holding all five stages, named by its stage suffix."""
    names = set()
    for root in roots if roots is not None else intrinsic_roots():
        if not os.path.isdir(root):
            continue
        found: dict[str, set] = {}
        for name in os.listdir(root):
            match = _STAGE.match(name)
            if match:
                found.setdefault(match.group(2) or 'v2', set()).add(int(match.group(1)))
        names.update(release for release, stages in found.items() if stages == {0, 1, 2, 3, 4})
    return sorted(names) or ['none found']


def stage_paths(release: str, roots=None) -> list[str]:
    for root in roots if roots is not None else intrinsic_roots():
        suffix = '' if release == 'v2' else f'_{release}'
        paths = [os.path.join(root, f'stage_{stage}{suffix}.pt') for stage in range(5)]
        if all(os.path.isfile(path) for path in paths):
            return paths
    raise FileNotFoundError(f"intrinsic release '{release}' needs stage_0..stage_4 files under "
                            f"{', '.join(roots if roots is not None else intrinsic_roots()) or 'models/intrinsic'}.")


def load_release(release: str, device: str):
    key = (release, device)
    if key not in _CACHE:
        try:
            from intrinsic.pipeline import load_models
        except ImportError as error:
            raise RuntimeError("the 'intrinsic' package is not installed (pip install "
                               "git+https://github.com/compphoto/Intrinsic); see this module's docstring.") from error
        # v2.1's albedo network adds its input back (alb_residual), v2.0's does not.
        paths = stage_paths(release)
        _CACHE.clear()
        with _no_console_prompts():
            _CACHE[key] = load_models(paths, device=device, alb_residual=release != 'v2')
    return _CACHE[key]


@contextlib.contextmanager
def _no_console_prompts():
    """Fail loud where a dependency would wait on a console answer nobody can give.

    The pipeline's backbones come through ``torch.hub.load``, which asks on stdin before fetching a repository missing
    from ``<torch.hub.get_dir()>/trusted_list``; inside ComfyUI that question blocks the executor for good.
    """
    def refuse(prompt=''):
        raise RuntimeError(f'intrinsic layers: a dependency asked for console input, which ComfyUI cannot give: '
                           f'{str(prompt).strip()} For a torch hub repository, add its owner_name line to '
                           f"{os.path.join(torch.hub.get_dir(), 'trusted_list')} and run again.")

    original = builtins.input
    builtins.input = refuse
    try:
        yield
    finally:
        builtins.input = original


def to_display(linear: np.ndarray) -> np.ndarray:
    linear = np.clip(linear, 0, None)
    return np.where(linear <= 0.0031308, 12.92 * linear, 1.055 * np.power(linear, 1 / 2.4) - 0.055)


def decompose(image: torch.Tensor, release: str, *, resize_conf: float | None = 0.0, base_size: int = 384,
              device: str | None = None) -> tuple[dict, dict]:
    """Decompose one [1,H,W,C] display image; return ({layer: float32 [H,W,3] linear at source size}, report)."""
    from intrinsic.pipeline import run_pipeline

    device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
    models = load_release(release, device)
    source = image[0, ..., :3].detach().to(device='cpu', dtype=torch.float32).numpy().astype(np.float32)
    height, width = source.shape[:2]
    results = run_pipeline(models, source, resize_conf=resize_conf, base_size=base_size, device=device)
    layers = {}
    for key, name in (('hr_alb', 'albedo'), ('dif_shd', 'diffuse_shading'), ('residual', 'residual'),
                      ('lin_img', 'linear_image')):
        layer = np.asarray(results[key], dtype=np.float32)
        if layer.ndim == 2:
            layer = np.repeat(layer[..., None], 3, axis=-1)
        if layer.shape[:2] != (height, width):
            tensor = torch.from_numpy(layer).permute(2, 0, 1)[None]
            layer = torch.nn.functional.interpolate(tensor, size=(height, width), mode='bilinear',
                                                    align_corners=False)[0].permute(1, 2, 0).numpy()
        layers[name] = layer
    worked = np.asarray(results['image']).shape[:2]
    report = {'schema': SCHEMA, 'release': release, 'size': [width, height], 'worked_at': [worked[1], worked[0]],
              'resize_conf': resize_conf, 'base_size': base_size, 'device': device,
              'layers': {name: {'mean': [float(v) for v in layer.reshape(-1, 3).mean(0)],
                                'max': float(layer.max()), 'min': float(layer.min())}
                         for name, layer in layers.items()}}
    return layers, report
