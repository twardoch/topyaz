---
title: Video AI (video)
layout: default
nav_order: 5
---

# `video` — Video AI

Upscale, denoise, stabilize, and interpolate video. `topyaz` drives the `ffmpeg`
build that ships inside Video AI, so its Topaz filters are available as flags.

```bash
topyaz video INPUT [flags]
```

`INPUT` is a single video file or a directory of them.

## Example

```bash
# Upscale 2x with the Artemis medium-quality model
topyaz video ./clips --model=amq-13 --scale=2 --output=./out

# Double the frame rate and stabilize
topyaz video shaky.mov --interpolate --fps=60 --stabilize
```

## Flags

| Flag | Default | Meaning |
|---|---|---|
| `--model` | `amq-13` | Enhancement model (see below). |
| `--scale` | `2` | Upscale factor. |
| `--fps` | — | Target frame rate (drives interpolation). |
| `--codec` | `hevc_videotoolbox` | Output codec. |
| `--quality` | `18` | Encoder quality (lower is higher quality). |
| `--denoise` | — | Noise reduction, 1–100. |
| `--details` | — | Detail recovery, 1–100. |
| `--halo` | — | Halo reduction, 1–100. |
| `--blur` | — | Deblur strength, 1–100. |
| `--compression` | — | Compression-artifact recovery, 1–100. |
| `--custom_filters` | — | Raw ffmpeg filter string, passed through verbatim. |
| `--device` | `0` | GPU device index (`-1` for CPU). |
| `--output` | — | Output file or directory. |
| `--stabilize` | off | Enable stabilization. |
| `--interpolate` | off | Enable frame interpolation. |

## Models

`--model` takes Topaz's model codes. The Artemis medium-quality family (`amq-13`
down to `amq-6`) is the general-purpose default; newer numbers are newer models.
Video AI also ships Proteus, Gaia, and other families — pass their codes directly.
Run `topyaz info` to confirm your Video AI install and its bundled models.

{: .note }
> `--custom_filters` is an escape hatch: whatever you pass is handed to ffmpeg
> unchanged. Use it for filters `topyaz` does not expose yet.
