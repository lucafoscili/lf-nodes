# Generated face fixture

`portrait-a.png` and `portrait-b.png` are 512 x 512 RGB close-ups of the same
fictional adult, generated locally for `model.face-align-identity` on
2026-11-05. No reference photograph, named person, LoRA or identity adapter was
used. The PNGs contain only pixels, with lossless compression and no metadata.

## Model and output publication

The generator is [Tongyi-MAI Z-Image-Turbo](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo),
using the [Comfy-Org single-file distribution](https://huggingface.co/Comfy-Org/Z-Image-Turbo).
Both model cards identify **Apache-2.0**. The
[upstream licence](https://github.com/Tongyi-MAI/Z-Image/blob/main/LICENSE)
permits use and redistribution and contains no restriction on publishing
generated outputs. It does not assign copyright in outputs or require generated
images to be licensed as model weights. These fictional outputs may therefore
be published as public test fixtures; no model weights are redistributed here.

Model files used, relative to ComfyUI's model folders:

| Component | File | SHA-256 |
| --- | --- | --- |
| Z-Image-Turbo BF16 | `diffusion_models/z_image_turbo_bf16.safetensors` | `2407613050b809ffdff18a4ac99af83ea6b95443ecebdf80e064a79c825574a6` |
| Qwen3 4B text encoder | `text_encoders/qwen_3_4b.safetensors` | `6c671498573ac2f7a5501502ccce8d2b08ea6ca2f661c458e708f36b36edfc5a` |
| Z-Image autoencoder | `vae/Zimage_ae.safetensors` | `afc8e28272cd15db3919bacdb6918ce9c1ed22e96cb12c4d5ed0fba823529e38` |

## Generation recipe

Both images use seed **20261105**, `KSampler`, sampler **euler**, scheduler
**simple**, **9 steps**, CFG **1.0**, denoise **1.0**, and
`ModelSamplingAuraFlow` shift **3.0**. `CLIPLoader` uses type `lumina2`.
`EmptySD3LatentImage` is 512 x 512, batch size 1; `VAEDecode` produces RGB.
The negative conditioning is `ConditioningZeroOut` of the first positive
conditioning. `SaveImageWebsocket` returns the images without filesystem or
metadata content; PNG compression is then optimized losslessly.

The exact shared identity prompt is:

```text
Studio headshot photograph of one entirely fictional adult woman aged 35, oval face, hazel eyes, short curly dark brown hair, softly arched eyebrows, small straight nose, light freckles across the cheeks, warm medium skin, closed-mouth neutral expression, plain charcoal crew-neck shirt, solid pale gray background, face centered and filling most of the frame, both eyes clearly visible, natural skin texture, sharp focus, no text, no accessories.
```

Append one space and the corresponding lighting sentence:

| File | Prompt suffix |
| --- | --- |
| `portrait-a.png` | `Soft even frontal daylight.` |
| `portrait-b.png` | `Soft daylight from slightly to the left.` |

## Titanic use

The existing Titanic harness binds loader 676 to this directory with a load
cap of two. Its ordered image list feeds Face Align (671); the aligned crops
and metadata feed Face Identity (672), then JSON viewer 673.
The case requires real execution of both face nodes, durable alignment
previews, and a two-image ArcFace cosine matrix whose cross-image score is at
least 0.65. This is a fixture acceptance threshold, not a general biometric
identity decision threshold. The installed `antelopev2` InsightFace pack is
used only for the test; it is not included in this repository.
