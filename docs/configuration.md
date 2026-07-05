---
title: Configuration
layout: default
nav_order: 6
---

# Configuration

## Global options

These flags come *before* the command and apply to every product:

```bash
topyaz --verbose --dry_run --timeout=7200 giga ./photos --model=hf
```

| Option | Default | Meaning |
|---|---|---|
| `--output_dir` | — | Default output directory for all commands. |
| `--config_file` | `~/.topyaz/_config.yaml` | Path to a config file. |
| `--parallel_jobs` | `1` | Parallel job count (not yet implemented). |
| `--timeout` | `3600` | Per-command timeout, in seconds. |
| `--backup_originals` | off | Copy each original before processing it. |
| `--preserve_structure` | on | Mirror the input directory tree in the output. |
| `--dry_run` | off | Build and print the command without running it. |
| `--verbose` | off | Debug-level logging. |

`--dry_run` is the safe way to see exactly what `topyaz` will ask Topaz to do.

## Where settings come from

`topyaz` resolves configuration in this order, later sources winning:

1. Built-in defaults.
2. The config file at `~/.topyaz/_config.yaml`.
3. A file passed with `--config_file`.
4. Environment variables prefixed `TOPYAZ_`.
5. Flags on the command line.

## Config file

A YAML file lets you set executable paths and default parameters once:

```yaml
# ~/.topyaz/_config.yaml
executables:
  gigapixel: /Applications/Topaz Gigapixel AI.app/Contents/MacOS/gigapixel
  photo_ai: /Applications/Topaz Photo AI.app/Contents/MacOS/tpai
  video_ai: /Applications/Topaz Video AI.app/Contents/MacOS/ffmpeg

defaults:
  timeout: 3600
```

## Environment variables

Any setting can be supplied through a `TOPYAZ_`-prefixed variable, handy for CI or
containers where you would rather not commit a config file:

```bash
export TOPYAZ_TIMEOUT=7200
```

## Finding your Topaz executables

If a product will not resolve, run `topyaz info` to see what `topyaz` detected, then
set the correct path in the config file under `executables`. Paths differ between
macOS and Windows and between product versions, so pin them explicitly when the
defaults miss.
