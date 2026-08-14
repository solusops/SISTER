---
language:
  - en
license: cc-by-4.0
task_categories:
  - text-generation
tags:
  - creative-writing
  - instruction-following
  - text-generation
---

# SISTER Benchmark: Baseline Model Generations

*Dataset card for the private baseline-generations repository.*

## Summary

Raw model outputs collected by running
[`SolusOps/sister-benchmark`](https://huggingface.co/datasets/SolusOps/sister-benchmark)
against several open-weight models, in both the full-instruction and
sharded conditions. **One split per model.** A `generations_index.json`
file in this repo (not a dataset split) records run provenance: config
fingerprints, dataset hash, per-model progress, and integrity metadata.

## Fields

| field | type | description |
|---|---|---|
| `record_id` / `attempt_id` | string | unique IDs for the generation / attempt |
| `model_id` / `model_name` / `parameters` / `quant_file` | string | model identity |
| `condition` | string | `full` or sharded condition |
| `turn` / `sequence` | int | position within the run |
| `item` | dict | back-reference to the task (`domain`, `item_id`, `title`); join against `sister-benchmark` for the full instruction/shard text |
| `text` | string | the model's generated output |
| `metrics` | dict | token usage, elapsed time, finish reason |
| `is_final` | bool | whether this is the final turn's output |
| `created_at` | string | ISO timestamp |

## Loading

```python
from datasets import load_dataset, concatenate_datasets

one_model = load_dataset("SolusOps/sister-benchmark-generations",
                          split="qwen_qwen3_5_9b")

gens = load_dataset("SolusOps/sister-benchmark-generations")
all_generations = concatenate_datasets(list(gens.values()))
```

## Collection

Generations were produced locally via LM Studio / Ollama at temperature
0.8, seed 12345, 16,384-token context. Only responses that finished with
`stop` (i.e. not context-truncated) were kept as evidence.

## License

These generation records are licensed under
[Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## Citation

```bibtex
@misc{incremental_instruction_creative_writing_2026,
  title  = {The Effects of Incremental Instruction Delivery on Language-Model Creative Writing},
  author = {Anshuman Singh and Abrar Eyasir and Haseeb Yaqoob and John Manavalan},
  year   = {2026},
  note   = {Manuscript in preparation}
}
```
