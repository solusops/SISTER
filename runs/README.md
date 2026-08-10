# SISTER evaluation runs

This directory runs the fixed 160-item creative-writing benchmark against one
explicit local model at a time. It requires Python 3.10+ only; the evaluator
uses the standard library.

## Run a model

Start either LM Studio's local server or Ollama, then list the exact installed
model identifier:

```bash
python3 runs/run_experiment.py --backend lmstudio --list-models
python3 runs/run_experiment.py --backend ollama --list-models
```

Run one model with its exact identifier or tag:

```bash
python3 runs/run_experiment.py --backend lmstudio --models publisher/model-id
python3 runs/run_experiment.py --backend ollama --models model:tag
```

The normal run uses a 16,384-token context window, temperature 0.8, seed
12345, and one model at a time. The LM Studio run applies the verified local
load settings: one parallel slot, Flash Attention, GPU KV cache, and the
configured evaluation batches.

Use a small smoke test before a new full run:

```bash
python3 runs/run_experiment.py --backend lmstudio --models publisher/model-id --limit 3
```

## Continue a known run

Only continue a specific stopped run when its raw outputs and index are already
present in the active `runs/results/` directory:

```bash
python3 runs/run_experiment.py \
  --backend lmstudio \
  --models publisher/model-id \
  --continue-run-id RUN_ID \
  --seed 12345
```

To record an explicitly approved context change during continuation, add
`--context-length TOKENS`. The index keeps historical generation and context
segments. Do not use this for a fresh collaborator run unless the protocol
calls for it.

## Result contract

The active result root stays flat:

```text
runs/results/
  results_<model>.jsonl  # one file per completed model
  all_results.jsonl      # combined independent dataset
  index.json             # run metadata, progress, provenance, integrity
```

Every completed model must have 320 final conditions and 1,156 raw records.
Each raw row carries the model ID, display name, parameter count, quant file,
prompt/output metrics, and finish reason. The runner rejects a reply that does
not end with `stop`; it never records a context-truncated response as evidence.

Historical, partial, reasoning-mode, and diagnostic outputs belong under
`runs/test/older_outputs/`, never in the active flat result root.

## Merge collaborator outputs

When collaborators complete distinct models independently, merge their result
roots into a fresh destination:

```bash
python3 runs/merge_results.py collaborator_a/results collaborator_b/results --output merged_results
```

The merger validates duplicate models and record IDs, each source's raw files,
and the combined dataset before it creates a new flat output root.
