# `runs/hf_upload/`: publishing this repo's data to Hugging Face

Two local things map to two separate Hub repos. Different lifecycles, so
different scripts, run independently:

| local path | script | Hub repo | what it is |
|---|---|---|---|
| `runs/benchmark_data.json` | `push_benchmark.py` | `sister-benchmark` | the 160-task benchmark itself. Stable, versioned, reusable by anyone. |
| `runs/results/results_*.jsonl` + `index.json` | `push_generations.py` | `sister-benchmark-generations` | raw outputs from running the benchmark against our baseline models. Grows as we add models/runs. |

Why not one repo: the benchmark is the citable artifact, and its identity
needs to stay stable and independently versioned so someone else can pin
to "v1.0" and evaluate their own model against exactly those 160 tasks.
The generations are evidence from *this* paper's specific experiment, on
a different update cadence entirely. Coupling them would mean every
benchmark expansion and every new baseline run land in the same commit
history, making it unclear what a citation to "the benchmark" actually
points to. See `../BENCHMARK.md` and `../results/README.md` for more.

## Files here

- `push_benchmark.py`: pushes `runs/benchmark_data.json` to `sister-benchmark`.
- `push_generations.py`: pushes `runs/results/results_*.jsonl` (one split
  per model) + `index.json` to `sister-benchmark-generations`.
- `DATASET_CARD_benchmark.md`: paste into the `sister-benchmark` repo's README on the Hub.
- `DATASET_CARD_generations.md`: paste into the `sister-benchmark-generations` repo's README on the Hub.

## Links

- Benchmark: https://huggingface.co/datasets/SolusOps/sister-benchmark
- Generations: https://huggingface.co/datasets/SolusOps/sister-benchmark-generations

## New pushes: `push_dataset.py`

The two scripts above still describe how those two repos were built, and
they remain accurate (same 6 models, same 160 tasks) — they're kept, not
re-run. But going forward, citing the *full study* (benchmark + generations
+ judging + human validation) uses one new consolidated repo built by
`push_dataset.py` instead: six configs (`benchmark`, `generations`,
`pointwise_scores`, `pairwise_validation`, `evidence_first_validation`,
`human_eval`) in a single repo, named after the paper
(`incremental-instruction-creative-writing`) rather than after `SISTER`
(the program). See that script's docstring and
`DATASET_CARD.md` for the full config/file layout. The old two repos stay
published as legacy for existing citations; this one supersedes them for
new ones.
