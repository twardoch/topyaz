---
title: Photo AI (photo)
layout: default
nav_order: 4
---

# `photo` — Photo AI

Enhance photos: denoise, sharpen, upscale, and fix faces. By default Photo AI's
Autopilot decides what each image needs; you can override any part of it.

```bash
topyaz photo INPUT [flags]
```

`INPUT` is a single image or a directory.

## Example

```bash
# Let Autopilot handle a whole shoot
topyaz photo ./shoot --output=./enhanced

# Take manual control: strong denoise, no upscaling
topyaz photo noisy.raw --override_autopilot --noise --denoise_strength=80 --no-upscale
```

## How Autopilot and overrides interact

Run `topyaz photo INPUT` with no enhancement flags and Photo AI's Autopilot chooses
the settings — the common case. Pass `--override_autopilot` (or any specific strength
value) to take the wheel. The boolean toggles below turn individual stages on or off;
the `*_strength` and `*_model` flags tune each stage.

## Core flags

| Flag | Default | Meaning |
|---|---|---|
| `--preset` | `auto` | Named Photo AI preset, or `auto` for Autopilot. |
| `--format_output` | `preserve` | Output format: `preserve`, `jpg`, `png`, `tiff`, `dng`. |
| `--quality` | `95` | JPEG quality, 1–100. |
| `--compression` | `6` | PNG compression, 0–10. |
| `--bit_depth` | `8` | Output bit depth (`8` or `16`). |
| `--tiff_compression` | `lzw` | TIFF compression: `none`, `lzw`, `zip`. |
| `--output` | — | Output file or directory. |
| `--show_settings` | off | Print the resolved settings and exit without processing. |
| `--override_autopilot` | off | Ignore Autopilot and use the flags you pass. |

## Stage toggles (keyword flags)

Each is tri-state — omit to leave to Autopilot, `--upscale` to force on, `--no-upscale` to force off.

`--upscale`, `--noise`, `--sharpen`, `--lighting`, `--color`, `--adjust_color`,
`--overwrite_files`, `--recurse_directories`, `--append_filters`.

## Tuning flags

Face: `--face_strength`, `--face_detection`, `--face_parts`.

Denoise: `--denoise_model`, `--denoise_levels`, `--denoise_strength`, and the RAW
variants `--denoise_raw_model`, `--denoise_raw_levels`, `--denoise_raw_strength`.

Sharpen: `--sharpen_model`, `--sharpen_levels`, `--sharpen_strength`.

Upscale: `--upscaling_model`, `--upscaling_factor`, `--upscaling_type`,
`--deblur_strength`, `--denoise_upscale_strength`.

Light & color: `--lighting_strength`, `--raw_exposure_strength`,
`--temperature_value`, `--opacity_value`.

Resolution: `--resolution_unit`, `--default_resolution`.

{: .note }
> `--format_output` is the output-format flag (not `--format`). See the note on the
> [Gigapixel page](gigapixel.md#flags).
