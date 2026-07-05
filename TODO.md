# TODO

Flat, actionable backlog. See `PLAN.md` for the reasoning behind each item.

## Next

- [ ] Rename the `--format_output` / `--quality_output` flags to `--format` / `--quality`
      across `giga` and `photo` (keep old names as hidden aliases for one release),
      update tests, docs, and the preferences mapping.
- [ ] Publish `docs/` to GitHub Pages (enable Pages → "Deploy from a branch" on `docs/`).
- [ ] Add Topaz product-version detection and warn when an installed app's CLI differs
      from what topyaz expects (Topaz changes these between releases).

## Remote execution (designed, not shipped)

- [ ] Implement the SSH remote executor in `execution/` (upload → process → download).
- [ ] Deadline/timeout propagation and idempotent retries for remote jobs.
- [ ] Document remote setup once it works.

## Coverage & quality

- [ ] Raise test coverage on `products/*/api.py` command-construction paths.
- [ ] Add an `examples/` folder of runnable, mocked usage scripts that double as tests.
- [ ] Wire `--parallel_jobs` to a real batch executor (currently a no-op).
