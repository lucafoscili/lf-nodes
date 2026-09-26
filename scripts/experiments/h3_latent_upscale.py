"""Build an offline, paired H3 latent-upscale experiment from a Runner API graph."""

from __future__ import annotations

import argparse
from copy import deepcopy
import json
import math
from pathlib import Path


def build_graph(graph: dict, *, base_width=768, base_height=1024,
                target_width=1248, target_height=1664, second_steps=4,
                second_denoise=0.25,
                model_name="minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors",
                precision="bf16") -> dict:
    """Keep the Kitchen recipe; add experimental full-frame refinement and a baseline."""
    for size in (base_width, base_height, target_width, target_height):
        if type(size) is not int or not 64 <= size <= 4096 or size % 32:
            raise ValueError("Dimensions must be integers from 64 to 4096, aligned to 32.")
    if target_width < base_width or target_height < base_height:
        raise ValueError("Target dimensions must not downscale either axis.")
    if max(target_width / base_width, target_height / base_height) > 4:
        raise ValueError("Learned upscaling supports at most 4x per axis.")
    if type(second_steps) is not int or second_steps < 1:
        raise ValueError("second_steps must be a positive integer.")
    if isinstance(second_denoise, bool) or not math.isfinite(second_denoise) or not 0 < second_denoise <= 1:
        raise ValueError("second_denoise must be finite and in (0, 1].")
    if precision not in ("bf16", "fp16", "fp32") or not model_name.strip():
        raise ValueError("Choose an upscaler filename and bf16/fp16/fp32 precision.")
    expected = {"h3": "MiniMaxH3ReferenceToVideo", "sample": "SamplerCustomAdvanced",
                "guider": "BasicGuider", "noise": "RandomNoise",
                "sampler_select": "KSamplerSelect", "scheduler": "BasicScheduler",
                "decode_video": "VAEDecode", "decode_audio": "VAEDecodeAudio",
                "create_video": "CreateVideo", "save": "SaveVideo"}
    for name, kind in expected.items():
        if graph.get(name, {}).get("class_type") != kind:
            raise ValueError(f"Expected Runner node {name}: {kind}.")
    if any(name.startswith("experiment_") for name in graph):
        raise ValueError("Graph already contains experiment nodes.")
    sample = graph["sample"]["inputs"]
    if any(sample.get(key) != value for key, value in {
        "noise": ["noise", 0], "guider": ["guider", 0],
        "sampler": ["sampler_select", 0], "sigmas": ["scheduler", 0],
        "latent_image": ["h3", 1],
    }.items()):
        raise ValueError("Expected the existing Runner sampling connections.")
    if (graph["sampler_select"]["inputs"]["sampler_name"] != "res_multistep"
            or graph["scheduler"]["inputs"]["steps"] != 20):
        raise ValueError("This experiment expects the accepted res_multistep 20-step recipe.")
    result = deepcopy(graph)
    result["h3"]["inputs"].update(width=base_width, height=base_height)
    result["experiment_target_conditioning"] = deepcopy(result["h3"])
    result["experiment_target_conditioning"]["inputs"].update(width=target_width, height=target_height)
    model = deepcopy(result["guider"]["inputs"]["model"])
    result["experiment_schedule"] = {
        "class_type": "BasicScheduler", "inputs": {
            "model": model, "scheduler": "simple", "steps": second_steps,
            "denoise": second_denoise},
        "_meta": {"title": "Experimental refinement schedule (not an upstream recommendation)"}}
    result["experiment_upscale_params"] = {
        "class_type": "MMH3LatentUpscaleWithModelParams", "inputs": {
            "model_name": model_name, "width": target_width, "height": target_height,
            "device": "cuda", "precision": precision, "keep_models_resident": False}}
    result["experiment_upscale"] = {
        "class_type": "MMH3UltimateUpscale", "inputs": {
            "model": deepcopy(model), "conditioning": ["experiment_target_conditioning", 0],
            "latent": ["sample", 1], "noise": deepcopy(sample["noise"]),
            "sampler": deepcopy(sample["sampler"]), "sigmas": ["experiment_schedule", 0],
            "cfg": 1.0, "latent_upscale_param": ["experiment_upscale_params", 0]}}
    # Share the original audio decode explicitly; no second audio decode or new VAE loader.
    result["experiment_baseline_decode"] = deepcopy(result["decode_video"])
    result["experiment_baseline_create"] = deepcopy(result["create_video"])
    result["experiment_baseline_create"]["inputs"]["images"] = ["experiment_baseline_decode", 0]
    result["experiment_baseline_save"] = deepcopy(result["save"])
    result["experiment_baseline_save"]["inputs"]["video"] = ["experiment_baseline_create", 0]
    prefix = result["save"]["inputs"]["filename_prefix"]
    result["experiment_baseline_save"]["inputs"]["filename_prefix"] = prefix + "-baseline"
    result["save"]["inputs"]["filename_prefix"] = prefix + "-latent-upscale"
    result["decode_video"]["inputs"]["samples"] = ["experiment_upscale", 0]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Existing Runner API graph JSON (not UI workflow JSON)")
    parser.add_argument("output", type=Path, help="New experiment API graph JSON; must not exist")
    for name, default in (("base-width", 768), ("base-height", 1024),
                          ("target-width", 1248), ("target-height", 1664), ("second-steps", 4)):
        parser.add_argument("--" + name, type=int, default=default)
    parser.add_argument("--second-denoise", type=float, default=0.25)
    parser.add_argument("--model-name", default="minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors")
    parser.add_argument("--precision", choices=("bf16", "fp16", "fp32"), default="bf16")
    args = vars(parser.parse_args())
    source, target = args.pop("input"), args.pop("output")
    result = build_graph(json.loads(source.read_text(encoding="utf-8-sig")), **args)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(f"Wrote experiment graph: {target.resolve()}")


if __name__ == "__main__":
    main()
