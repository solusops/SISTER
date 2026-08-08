# Running evaluations

Run commands from the repository root. The evaluator has a fixed 16,384-token
context cap. For LM Studio it uses one parallel slot, Flash Attention, GPU KV
cache, and disables reasoning only for models that explicitly support an
`off` setting; GPT-OSS receives no reasoning field because it does not support
`off`. There is no tracked model sequence: choose the exact model or models to
run.

## LM Studio

List the model IDs exposed by LM Studio:

```bash
python3 runs/run_experiment.py --backend lmstudio --list-models
```

Run one model:

```bash
python3 runs/run_experiment.py --backend lmstudio --models openai/gpt-oss-20b
```

Run several specific models in order:

```bash
python3 runs/run_experiment.py --backend lmstudio --models MODEL_A MODEL_B
```

## Ollama

Start Ollama and pull the model first. List available tags:

```bash
python3 runs/run_experiment.py --backend ollama --list-models
```

Run one tag:

```bash
python3 runs/run_experiment.py --backend ollama --models MODEL_TAG
```

Set `OLLAMA_BASE_URL` if Ollama is not at `http://localhost:11434`.

## Resume and outputs

Use `--resume` only for an interrupted run with the same model and settings.
Results are written immediately to `results/results_<model>.jsonl`,
`results/all_results.jsonl`, and `results/index.json`.

## Merge collaborator results

After collaborators complete different models, merge their result directories:

```bash
python3 runs/merge_results.py \
  --output merged_results \
  collaborator_a/results collaborator_b/results
```

The merge validates each source and creates fresh per-model JSONL files, one
combined dataset, and one rebuilt index.
