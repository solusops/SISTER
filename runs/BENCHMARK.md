# `benchmark_data.json` — what this file actually is

This file is not "input data for the runner." It's the benchmark itself:
the fixed, citable artifact this project defines and expects others to
reuse independently of your own experiments.

- 160 creative-writing tasks, 6 genres.
- Each task ships two ways: `full_instruction` (one complete prompt) and
  `shards` (the same task split into sequential turns).
- Published on Hugging Face as its own dataset repo:
  `YOUR_USERNAME/sister-benchmark` — see `runs/hf_upload/README.md`.

## Why it lives in `runs/` right now

`run_experiment.py` resolves this file relative to its own location
(`Path(__file__).resolve().parent / "benchmark_data.json"`), so it has to
stay next to the runner unless that constant is updated. It is *not*
conceptually part of `runs/results/` — think of it as a versioned input
the runner reads, not an output the runner produces.

## Versioning

Treat every change to the task set as a release, not a silent edit:

| version | tasks | notes |
|---|---|---|
| v1.0 | 160 | initial release, 6 genres |

When you expand the benchmark, bump this table and tag the corresponding
commit/push to `sister-benchmark` on the Hub (e.g. `v1.1`). Generations
already collected stay valid against the version they were run on —
`runs/results/index.json` records the exact `sha256` of the
`benchmark_data.json` used for each run, so provenance is preserved even
as the benchmark grows.
