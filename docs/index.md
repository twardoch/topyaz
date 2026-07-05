---
title: Home
layout: default
nav_order: 1
---

# topyaz

One command line for three Topaz apps.
{: .fs-6 .fw-300 }

Gigapixel AI, Photo AI, and Video AI each ship their own interface. `topyaz` puts all
three behind a single command, so a folder of 400 images becomes one line in a script
instead of an afternoon of clicking.

```bash
topyaz giga ./photos --model=hf --scale=4
topyaz photo ./raw --preset=auto
topyaz video ./clips --model=amq-13 --scale=2
```

`topyaz` does not replace Topaz's AI. It drives the Topaz apps you already own,
calling their command-line entry points and passing your parameters through verbatim.
You keep the models and the licenses; you lose the clicking.

## What it gives you

- **One interface.** The same verbs — `giga`, `photo`, `video` — across all three products.
- **Batch by default.** Point a command at a file or a whole directory.
- **Every knob.** The full parameter set of each product, exposed as flags.
- **Honest failures.** When a Topaz binary is missing or a license is absent, the
  error tells you which app, why, and what to do next.

## Requirements

`topyaz` calls Topaz apps installed on your machine. You need the apps and their licenses:

- **macOS 11+** (Topaz's CLI support is Mac-first; Windows paths are configurable).
- **Gigapixel AI** — a **Pro license** is required for command-line access.
- **Photo AI** and **Video AI** — recent versions with their bundled CLI tools.
- 16 GB RAM and room for the AI models (tens of GB per product).

## Start here

1. [Installation](installation.md) — install `topyaz` and point it at your Topaz apps.
2. [Gigapixel AI](gigapixel.md) — the `giga` command reference.
3. [Photo AI](photo.md) — the `photo` command reference.
4. [Video AI](video.md) — the `video` command reference.
5. [Configuration](configuration.md) — executable paths, defaults, and environment variables.

## Status

Local processing works today. Remote execution over SSH is designed but not yet
shipped. See the project [TODO](https://github.com/twardoch/topyaz/blob/main/TODO.md)
for what is landing next.
