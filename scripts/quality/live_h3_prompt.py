"""Opt-in live H3 authoring probe; never starts Comfy or renders video.

Loads the explicitly named downloaded LMS model, runs the public node, preserves
stage text for human review, and releases only an instance loaded by this probe.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.quality.run_pytests import _install_host_stubs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--idea", required=True)
    parser.add_argument("--reference", action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--no-review", action="store_true")
    parser.add_argument("--mode", choices=("auto", "t2va", "i2va", "fl2va", "l2va", "ref2va"), default="auto")
    parser.add_argument("--duration", type=float, default=6.0)
    args = parser.parse_args()
    if len(args.reference) > 9:
        parser.error("At most nine reference files are supported.")
    args.output.mkdir(parents=True, exist_ok=False)
    _install_host_stubs()

    import numpy as np
    import torch
    from PIL import Image
    from modules.nodes.llm import h3_prompt_maker as h3
    from modules.nodes.llm.lm_studio_models import LF_LMSLoadModel, LF_LMSUnloadModel
    from modules.utils.helpers.api.lm_studio_lifecycle import _inventory

    images = []
    sources = []
    for name in args.reference:
        source = Path(name).resolve(strict=True)
        with Image.open(source) as opened:
            pixels = np.array(opened.convert("RGBA" if "A" in opened.getbands() else "RGB"))
        images.append(torch.from_numpy(pixels.astype(np.float32) / 255.0).unsqueeze(0))
        sources.append({"path": str(source), "shape": list(images[-1].shape)})

    def save(name, data):
        (args.output / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    original_request = h3.request_local_chat_completion
    stages = []

    def observe(**kwargs):
        started = time.monotonic()
        number = len(stages) + 1
        print(f"Provider call {number} started", flush=True)
        text, response = original_request(**kwargs)
        stage = {"call": number, "seconds": round(time.monotonic() - started, 2), "text": text}
        for key in ("stats", "usage", "model_instance_id"):
            if key in response:
                stage[key] = response[key]
        stages.append(stage)
        save("stages.json", stages)
        print(f"Provider call {number} completed in {stage['seconds']}s", flush=True)
        return text, response

    h3.request_local_chat_completion = observe
    save("request.json", {"model": args.model, "idea": args.idea, "references": sources,
                          "review": not args.no_review, "mode": args.mode, "duration": args.duration})
    existing = {instance["id"] for model in _inventory(args.url, 15)
                for instance in model["loaded_instances"]}
    instance_id = None
    prompt = ""
    started = time.monotonic()
    try:
        print("Loading/reusing exact model", flush=True)
        instance_id, = LF_LMSLoadModel().on_exec([args.model], [args.url])
        save("lifecycle.json", {"instance_id": instance_id, "owned": instance_id not in existing})
        kwargs = {"intent": [args.idea], "url": [args.url], "model": [instance_id],
                  "mode": [args.mode], "duration_seconds": [args.duration], "review": [not args.no_review]}
        for number, pixels in enumerate(images, 1):
            kwargs["image" if number == 1 else f"image_{number}"] = [pixels]
        result = h3.LF_H3PromptMaker().on_exec(**kwargs)
        prompt, report, receipt = result["result"]
        (args.output / "prompt.txt").write_text(prompt, encoding="utf-8")
        save("result.json", {"seconds": round(time.monotonic() - started, 2),
                             "validation_report": report, "reference_receipt": receipt,
                             "history_matches": result["ui"]["lf_output"][0]["value"] == prompt})
        print(f"Complete: {args.output / 'prompt.txt'}", flush=True)
        return 0
    except Exception as error:
        save("failure.json", {"type": type(error).__name__, "message": str(error)})
        raise
    finally:
        if instance_id is not None and instance_id not in existing:
            print("Unloading probe-owned instance", flush=True)
            released, = LF_LMSUnloadModel().on_exec([prompt], [instance_id], [args.url])
            assert released == prompt
            remaining = {instance["id"] for model in _inventory(args.url, 15)
                         for instance in model["loaded_instances"]}
            save("lifecycle.json", {"instance_id": instance_id, "owned": True,
                                    "unloaded": instance_id not in remaining})
            if instance_id in remaining:
                raise RuntimeError("Probe instance is still loaded after the unload request.")
            print("Probe-owned instance unloaded", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
