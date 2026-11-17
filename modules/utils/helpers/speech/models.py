"""The speech models LF's Speech nodes run.

Each is read from a pinned Hugging Face snapshot (repository and revision, downloaded once into the Hugging Face
cache), loaded for one run on ComfyUI's device after ComfyUI frees room for it, and let go when the run ends, so a
speech run never leaves weights behind for the next workflow. Every heavy import happens inside these functions.
"""

from __future__ import annotations

import random
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np
import torch

# Each family's models, by Hugging Face repository, with the revision the nodes were written against.
SPEAKERS = {"k2-fsa/OmniVoice": "c5fdb5ccb189668d56333f77ba2629f4cd7535f4"}
CONVERTERS = {"ResembleAI/chatterbox": "5bb1f6ee58e50c3b8d408bc82a6d3740c2db6e18"}
SPEAKER_ENCODERS = {"microsoft/wavlm-base-plus-sv": "feb593a6c23c1cc3d9510425c29b0a14d2b07b1e"}
RECOGNIZERS = {"openai/whisper-large-v3-turbo": "41f01f3fe87f28c78e2fbf8b568835947dd65ed9"}

# What ComfyUI frees on the device before each loads (weights and working memory, rounded up).
_ROOM = {
    "k2-fsa/OmniVoice": 6 << 30,
    "ResembleAI/chatterbox": 3 << 30,
    "microsoft/wavlm-base-plus-sv": 1 << 30,
    "openai/whisper-large-v3-turbo": 4 << 30,
}
OMNIVOICE_RATE = 24000
CHATTERBOX_REFERENCE_SECONDS = 10.0  # ChatterboxVC.DEC_COND_LEN: the target voice it reads
S3GEN_BUILT = frozenset({"tokenizer.window"})  # the one S3Gen tensor its weights leave out: a window it computes
WAVLM_RATE = WHISPER_RATE = 16000


def loaded_whole(report, built: frozenset, repo: str) -> None:
    """A non-strict `load_state_dict`'s report, refused unless it left out only the tensors the model builds itself:
    weights that moved at a revision would otherwise run half loaded and say noise."""
    missing = sorted(set(report.missing_keys) - built)
    if missing or report.unexpected_keys:
        raise RuntimeError(f"{repo}'s weights do not fit its model: missing {missing[:5]} ({len(missing)}), "
                           f"unexpected {list(report.unexpected_keys)[:5]} ({len(report.unexpected_keys)}).")


def revision_of(family: dict, repo: str, revision: str) -> str:
    """The revision asked for `repo`, which must be one of `family`'s; an empty revision is refused, never `main`."""
    if repo not in family:
        raise ValueError(f"{repo!r} is not one of {', '.join(family)}.")
    if not isinstance(revision, str) or not revision.strip():
        raise ValueError(f"{repo} needs a revision (a commit of its Hugging Face repository).")
    return revision.strip()


def snapshot(repo: str, revision: str, patterns: list[str] | None = None) -> Path:
    """The local folder of `repo` at `revision`, fetched into the Hugging Face cache if it is not there yet."""
    from huggingface_hub import snapshot_download

    return Path(snapshot_download(repo, revision=revision, allow_patterns=patterns))


def device() -> torch.device:
    try:
        from comfy import model_management
    except ImportError:
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return model_management.get_torch_device()


@contextmanager
def running(repo: str):
    """ComfyUI's device with room made for `repo`; its cache emptied after, whatever happened."""
    target = device()
    try:
        from comfy import model_management
    except ImportError:
        model_management = None
    if model_management is not None:
        model_management.free_memory(_ROOM[repo] + model_management.minimum_inference_memory(), target)
    try:
        yield target
    finally:
        if model_management is not None:
            model_management.soft_empty_cache()
        elif torch.cuda.is_available():
            torch.cuda.empty_cache()


def seeded(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed % (2**32))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def omnivoice_speak(text: str, *, revision: str, language: str, seed: int, num_step: int, guidance_scale: float,
                    speed: float, reference: tuple[torch.Tensor, int] | None = None, reference_text: str = "",
                    design: str = "") -> tuple[np.ndarray, int, dict]:
    """OmniVoice saying `text`: in the voice of `reference` (with its transcript), or of the voice `design` describes."""
    repo = "k2-fsa/OmniVoice"
    folder = snapshot(repo, revision)
    from omnivoice import OmniVoice

    started = time.perf_counter()
    with running(repo) as target:
        model = OmniVoice.from_pretrained(str(folder), device_map=str(target),
                                          dtype=torch.float16 if target.type == "cuda" else torch.float32)
        loaded = time.perf_counter()
        try:
            seeded(seed)
            options = dict(language=language or None, num_step=num_step, guidance_scale=guidance_scale,
                           speed=speed if speed > 0 else None)
            if reference is not None:
                prompt = model.create_voice_clone_prompt(ref_audio=reference, ref_text=reference_text)
                audio = model.generate(text=text, voice_clone_prompt=prompt, **options)
            else:
                audio = model.generate(text=text, instruct=design, **options)
            rate = int(getattr(model, "sampling_rate", OMNIVOICE_RATE))
        finally:
            del model
    done = time.perf_counter()
    return np.asarray(audio[0], dtype=np.float32), rate, {
        "load_seconds": round(loaded - started, 2), "run_seconds": round(done - loaded, 2)}


def chatterbox_convert(source: torch.Tensor, source_rate: int, target: torch.Tensor, target_rate: int, *,
                       revision: str) -> tuple[torch.Tensor, int, dict]:
    """Chatterbox's voice conversion: `source`'s words and timing in the voice of `target` (its first ten seconds).
    The output carries Resemble's Perth watermark, as Chatterbox's own conversion does."""
    from .audio import resampled

    repo = "ResembleAI/chatterbox"
    folder = snapshot(repo, revision, ["s3gen.safetensors"])
    import perth
    from chatterbox.models.s3gen import S3GEN_SR, S3Gen
    from chatterbox.models.s3tokenizer import S3_SR
    from safetensors.torch import load_file

    started = time.perf_counter()
    with running(repo) as where:
        model = S3Gen()
        loaded_whole(model.load_state_dict(load_file(folder / "s3gen.safetensors"), strict=False), S3GEN_BUILT, repo)
        model.to(where).eval()
        loaded = time.perf_counter()
        try:
            voice = resampled(target, target_rate, S3GEN_SR)[: int(CHATTERBOX_REFERENCE_SECONDS * S3GEN_SR)]
            with torch.inference_mode():
                reference = model.embed_ref(voice.to(where), S3GEN_SR, device=where)
                spoken = resampled(source, source_rate, S3_SR).to(where)[None]
                tokens, _ = model.tokenizer(spoken)
                converted, _ = model.inference(speech_tokens=tokens, ref_dict=reference)
            converted = converted.squeeze(0).detach().cpu().numpy()
        finally:
            del model
    marked = perth.PerthImplicitWatermarker().apply_watermark(converted, sample_rate=S3GEN_SR)
    done = time.perf_counter()
    return torch.from_numpy(np.asarray(marked, dtype=np.float32)), S3GEN_SR, {
        "load_seconds": round(loaded - started, 2), "run_seconds": round(done - loaded, 2),
        "target_seconds_read": round(min(voice.shape[-1] / S3GEN_SR, CHATTERBOX_REFERENCE_SECONDS), 3),
        "watermark": "perth-implicit"}


def speaker_similarity(audio: torch.Tensor, audio_rate: int, reference: torch.Tensor, reference_rate: int, *,
                       repo: str, revision: str) -> tuple[float, dict]:
    """The cosine of the two recordings' speaker embeddings (WavLM x-vectors): 1 the same voice."""
    from .audio import resampled

    folder = snapshot(repo, revision)
    from transformers import AutoFeatureExtractor, WavLMForXVector

    started = time.perf_counter()
    with running(repo) as where:
        extractor = AutoFeatureExtractor.from_pretrained(str(folder))
        model = WavLMForXVector.from_pretrained(str(folder)).to(where).eval()
        try:
            clips = [resampled(audio, audio_rate, WAVLM_RATE).numpy(), resampled(reference, reference_rate, WAVLM_RATE).numpy()]
            embeddings = []
            for clip in clips:  # one at a time: padding a short clip to a long one moves its embedding
                inputs = extractor(clip, sampling_rate=WAVLM_RATE, return_tensors="pt").to(where)
                with torch.inference_mode():
                    embeddings.append(model(**inputs).embeddings[0].float().cpu())
        finally:
            del model
    cosine = torch.nn.functional.cosine_similarity(embeddings[0], embeddings[1], dim=-1).item()
    return round(float(cosine), 4), {"seconds": round(time.perf_counter() - started, 2)}


def transcribe(audio: torch.Tensor, audio_rate: int, *, repo: str, revision: str, language: str) -> tuple[str, dict]:
    """What Whisper hears in the recording."""
    from .audio import resampled

    folder = snapshot(repo, revision)
    from transformers import WhisperForConditionalGeneration, WhisperProcessor

    started = time.perf_counter()
    with running(repo) as where:
        processor = WhisperProcessor.from_pretrained(str(folder))
        dtype = torch.float16 if where.type == "cuda" else torch.float32
        model = WhisperForConditionalGeneration.from_pretrained(str(folder), torch_dtype=dtype).to(where).eval()
        try:
            features = processor(resampled(audio, audio_rate, WHISPER_RATE).numpy(), sampling_rate=WHISPER_RATE,
                                 return_tensors="pt").input_features.to(where, dtype)
            with torch.inference_mode():
                tokens = model.generate(features, language=language or None, task="transcribe")
            heard = processor.batch_decode(tokens, skip_special_tokens=True)[0].strip()
        finally:
            del model
    return heard, {"seconds": round(time.perf_counter() - started, 2)}
