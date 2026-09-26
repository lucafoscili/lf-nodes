# H3 learned latent upscale experiment

Question: can the accepted Kitchen/res_multistep 20-step reference recipe deliver
useful ~2 MP detail faster by generating a smaller latent, learning its spatial
upscale, then refining briefly? This is a local candidate, not production wiring.
Decision: **keep as a candidate**, defer promotion to the default renderer.
The [2026-09-26 paired trial](../../docs/llm/h3-latent-upscale-trial.md) succeeded
and added subject detail, but also redrew small facial/jewelry features. The
accepted phone orchestra remains unchanged.

`h3_latent_upscale.py` accepts a configured Runner reference API graph and creates
a new graph without importing Comfy, contacting a provider, or submitting work.
The original prompt, reference images, model chain, first-pass schedule, frame
count, seed and FPS are retained. Defaults preserve the accepted portrait 3:4
orientation: 768×1024 (0.786 MP, approximately the requested 0.7 MP) to 1248×1664
(2.077 MP). Explicit CLI dimensions support other orientations.

The new full-frame second pass uses the same Kitchen model and res_multistep
sampler. Its simple schedule, four steps and 0.25 denoise are **experimental local
choices**, not upstream recommendations. The wrapper's supplied Turbo example
uses a different model/sampler/schedule and is not a controlled comparison.

Install only `benjiyaya/ComfyUI-MinimaxH3-Latent-Upres`; it embeds the learned
upscaler. Its `MMH3UltimateUpscale` accepts the first sampler's denoised AV latent,
fresh target-resolution conditioning from the original references, and
`MMH3LatentUpscaleWithModelParams`. No splitting, tiling, Turbo LoRA, or new VAE
loader is added. The wrapper preserves original latent audio; both saved videos
also explicitly share the original audio decoder, ensuring identical audio
input to muxing. Original video decode becomes high-resolution, with one cloned
low-resolution video decoder and distinct `-baseline`/`-latent-upscale` prefixes.
No extra unload nodes are introduced; actual scheduling/memory remains Comfy's.

Place `minimax_h3_latent_upscaler_3d_conv_v1_bf16.safetensors` in
`ComfyUI/models/latent_upscale_models/`. Filename and inference precision are
configurable. High-resolution refinement can still require substantial VRAM.

```powershell
python scripts/experiments/h3_latent_upscale.py accepted-api.json experiment-api.json
python scripts/experiments/h3_latent_upscale.py --help
python scripts/experiments/test_h3_latent_upscale.py
```

The output file must be new. These structural tests prove wiring and input
preservation only; they do not establish quality, audio playback, timing or GPU
compatibility. Keep source reference media and existing accepted outputs intact.
