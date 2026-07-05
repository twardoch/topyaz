---
title: Installation
layout: default
nav_order: 2
---

# Installation

## Install topyaz

```bash
pip install topyaz
```

Or, for an isolated tool install:

```bash
uv tool install topyaz
```

Confirm it landed:

```bash
topyaz version
```

## Install the Topaz apps

`topyaz` is a wrapper. It runs the Topaz apps you already have, so install them first:

| Product | What topyaz calls | License note |
|---|---|---|
| Gigapixel AI | the bundled `gigapixel` CLI | **Pro license required** for CLI use |
| Photo AI | the `tpai` command-line tool | standard license |
| Video AI | the `ffmpeg` build shipped with Video AI | standard license |

On macOS these live inside the app bundles under `/Applications`. `topyaz` looks for
them there by default. If yours are elsewhere, point to them — see
[Configuration](configuration.md).

## Check what topyaz can see

Before processing anything, ask `topyaz` what it found:

```bash
topyaz info
```

This reports your platform, detected GPU and memory, and which Topaz executables
resolved. If a product shows as missing, fix the path before running its command.

## From source

```bash
git clone https://github.com/twardoch/topyaz
cd topyaz
uv venv && source .venv/bin/activate
uv pip install -e ".[dev,test]"
python -m pytest
```
