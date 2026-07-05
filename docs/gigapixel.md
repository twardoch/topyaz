---
title: Gigapixel AI (giga)
layout: default
nav_order: 3
---

# `giga` — Gigapixel AI

Upscale and enhance images. Requires a **Gigapixel AI Pro** license for CLI access.

```bash
topyaz giga INPUT [flags]
```

`INPUT` is a single image or a directory. A directory is processed file by file.

## Example

```bash
# Upscale a folder 4x with the high-fidelity model
topyaz giga ./photos --model=hf --scale=4 --output=./out

# Restore a low-resolution scan and recover faces
topyaz giga old_scan.jpg --model=recovery --face_recovery=80
```

## Flags

| Flag | Default | Meaning |
|---|---|---|
| `--model` | `std` | Enhancement model — see the table below. |
| `--scale` | `2` | Upscale factor (2, 4, 6…). |
| `--denoise` | — | Noise reduction, 1–100. |
| `--sharpen` | — | Sharpening, 1–100. |
| `--compression` | — | Compression-artifact recovery, 1–100. |
| `--detail` | — | Detail enhancement, 1–100. |
| `--creativity` | — | Generative creativity (Redefine model), 1–6. |
| `--texture` | — | Texture strength (Redefine model), 1–6. |
| `--prompt` | — | Text prompt for generative models. |
| `--face_recovery` | — | Face recovery strength, 1–100. |
| `--face_recovery_version` | `2` | Face-recovery model version. |
| `--format_output` | `preserve` | Output format: `preserve`, `jpg`, `png`, `tiff`. |
| `--quality_output` | `95` | JPEG quality, 1–100. |
| `--bit_depth` | `0` | Output bit depth (`0` keeps the source). |
| `--parallel_read` | `1` | Concurrent file reads. |
| `--output` | — | Output file or directory (defaults beside the input). |

{: .note }
> The flags are named `--format_output` and `--quality_output` (not `--format` /
> `--quality`). This is a known naming wart carried by the current release; a rename
> is on the [TODO](https://github.com/twardoch/topyaz/blob/main/TODO.md).

## Models

`--model` accepts any of these names (aliases group together):

| Model | Aliases | Best for |
|---|---|---|
| Standard | `std`, `standard` | General-purpose upscaling |
| High Fidelity | `hf`, `fidelity`, `high fidelity` | Clean, high-quality sources |
| Low Resolution | `low`, `lowres`, `low res`, `low resolution` | Small or web-sized images |
| Art & CG | `art`, `cg`, `cgi`, `lines` | Illustration, renders, line art |
| Compression | `compression`, `vc`, `very compressed`, `high compression` | Heavily compressed JPEGs |
| Text | `text`, `txt`, `text refine` | Documents and screenshots |
| Recovery | `recovery` | Very low-detail restoration |
| Redefine | `redefine` | Generative detail (uses `--creativity`, `--texture`, `--prompt`) |
