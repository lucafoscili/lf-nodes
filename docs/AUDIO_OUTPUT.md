# WAV output

`LF_SaveAudio` saves a ComfyUI `AUDIO` dictionary as one WAV file per batch
item, in source order. It runs without a frontend or a connected output socket.

Required inputs are `audio` and `filename_prefix` (default `audio/ComfyUI`).
The waveform must be a non-empty floating-point tensor shaped
`[batch, channels, samples]`, with one or two channels. `sample_rate` must be an
integer from 1 through 384000 Hz. Invalid shapes, rates, non-finite samples,
and unsafe prefixes fail before any output is written.

Files use IEEE float32 WAV (`pcm_f32le`). Samples are converted to float32 but
never clipped, normalized, trimmed, or resampled. Values outside `[-1, 1]`
are retained; playback devices may clip them. The saver does not make a
duration rounded by an upstream model sample-exact.

Outputs, in fixed socket order:

1. `output_reference`: a list of portable `relative/path.wav [output]`
   references, one per saved batch item.
2. `receipt`: an aggregate `lf.audio_file.receipt.v1` JSON object. Its ordered
   `files` list records index, relative `file_name`, `storage_type`, format,
   encoding, sample rate, channels, sample count, duration, and byte length.

Core's normal mapped-list execution applies. Every AUDIO batch is processed
independently; there is no cross-input list pairing or automatic concatenation.
Destinations must remain under ComfyUI output. Counter-based filenames and
exclusive file creation prevent overwriting an existing artifact. A failed
write removes its incomplete file; already completed batch items remain.

Native `ui.audio` records and `ui.lf_output` contain the same output artifacts.
The optional `LF_MASONRY` widget supplies playable audio controls from durable
output references, including after history hydration and saved-widget reload.
The live `lf-saveaudio` event mirrors the final history payload. There are no
temporary previews, embedded audio bytes, or extra audio normalization passes.

## Bounded live check — 2026-08-31

`stable_audio_3_sfx` generated four real candidates through the Runner with
Stable Audio 3 Medium: a 10-second hearth (seed 42) and three 3-second axe
takes (seeds 43–45). All four completed and decoded as finite stereo 44.1 kHz
float WAV; actual durations were 10.031 and 2.972 seconds. Core execution
times were 11.018 seconds cold and 2.350 / 1.662 / 1.791 seconds warm on an
RTX 4090. The largest sampled device-total memory reading was 5,466 MiB
(not a model allocator measurement or a guaranteed absolute peak).

The real Comfy history gallery played the hearth WAV. The LF node accepted
its actual Core history payload through `onExecuted`; serializing and
reloading that graph restored a playable WAV control. The Runner's exact
run page also played the same artifact before and after a full page reload.
This was a focused saver/workflow check, not a full Titanic execution.

These checks establish generation and playback mechanics, **not listening
approval**. The hearth contains a quiet tail and has not been accepted as
a seamless loop. All originals remain untrimmed; perceptual review and any
game-specific editing belong to the consumer audition.
