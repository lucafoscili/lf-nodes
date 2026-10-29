# PNG with stored values

`LF_LoadPNG` and `LF_SavePNG`, under **LF Nodes/IO Operations**, read and write
PNG files without changing their values, for workflows whose output must match
another tool's to the level: texture maps, masks kept as alpha, 16-bit data.

Core's `LoadImage` and `SaveImage` are made for pictures: they load 8-bit RGB,
turn alpha into an inverted `MASK`, and save with `clip(255 * x)` cast to
`uint8`, which truncates, so a value computed as 0.996 of a level comes back one
level low. They also embed the prompt in the file.

## Load PNG (`LF_LoadPNG`)

- `image`: a PNG in ComfyUI's input folder (with an upload button), an annotated
  `name.png [temp]` or `sub/name.png [output]` reference, or an absolute path.
- Outputs `image` (0..1 float, value / 255 or value / 65535), `alpha` (the stored
  alpha as a mask, not inverted; all ones without alpha), `bit_depth` (8 or 16),
  `receipt` (`lf.load-png.v1`: file, size, colour type, bit depth, sha256) and
  `image_list`.
- Alpha stays the image's fourth channel, so nodes that treat every channel
  alike (such as Edge padding) carry it through. Grey widens to RGB and grey with
  alpha to RGBA, values unchanged. Palette images expand to their colours, and
  1, 2 or 4-bit grey scales to 8 bits, as PNG defines. No colour management,
  gamma or orientation is applied.
- The widget shows the image in Masonry with its size, depth and colour type.

## Save PNG (`LF_SavePNG`)

- `image`, `filename_prefix` (output-relative, a counter and `.png` added),
  `bit_depth` (8 or 16: wire Load PNG's `bit_depth` to keep a file's depth) and
  `compress_level` (0 to 9; lossless at every level).
- Each value is clamped to 0..1 and rounded to the nearest level (half to even).
  Every value Load PNG produced comes back exactly, at either depth.
- RGB writes RGB, RGBA writes RGBA (alpha as alpha), one channel writes grey.
  The file holds only `IHDR`, `IDAT` and `IEND`: no prompt, workflow or other
  metadata. NaN or infinite values raise.
- Outputs `file_names` (output-relative, also published as `lf_output`
  `file_names`, so the Workflow Runner lists each file as an artifact) and
  `receipt` (`lf.save-png.v1`: per file its size, channels, depth, bytes and
  sha256). The widget shows the saved images in Masonry.

OpenCV does the coding, since Pillow cannot write 16-bit colour PNG.
