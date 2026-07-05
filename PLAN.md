# Plan

Where topyaz is going, and why. Task-level items live in `TODO.md`.

## Where it stands (v1.0.0)

Local processing works across all three products. The suite is green (176 tests,
Topaz binaries mocked), types check clean, CI runs lint + type-check + a 3.10–3.12
test matrix, and the docs describe the real command surface.

## 1. Fix the flag names

The current release exposes `--format_output` and `--quality_output` — the scars of a
global find-and-replace that also renamed the plain `format`/`quality` concepts. They
work, but they read wrong to anyone typing a command. Rename to `--format` and
`--quality`, keep the old spellings as hidden aliases for one release so no script
breaks, and update the tests, docs, and the Photo AI preferences mapping together.

## 2. Ship the docs

The `docs/` site is written; it needs to go live. Turn on GitHub Pages ("Deploy from a
branch", folder `docs/`) so `https://twardoch.github.io/topyaz` serves it.

## 3. Guard against Topaz drift

Topaz changes its CLI between product releases. topyaz should detect the installed
version of each product and warn — clearly, in the error channel — when it meets an
interface it was not built for, rather than failing deep inside a subprocess.

## 4. Remote execution

The architecture anticipates processing on a beefier remote machine over SSH. It is
designed but not built. When it lands it must treat partial failure as a real outcome:
propagate deadlines end to end, make each remote job idempotent, and retry with a
budget instead of hammering a struggling host.

## 5. Real batch parallelism

`--parallel_jobs` is accepted and ignored. Back it with an actual bounded executor so a
thousand-file directory uses the machine it is running on.
