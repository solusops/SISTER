---
language:
  - en
license: cc-by-4.0
task_categories:
  - text-generation
tags:
  - creative-writing
  - instruction-following
---

# SISTER Benchmark: Multi-Turn Instruction Sharding, Creative Writing

*Dataset card for the private benchmark repository.*

## Summary

160 creative-writing tasks across 6 genres, each provided in two forms:

- `full_instruction`: the task as one complete instruction.
- `shards`: the same task split into a sequence of smaller instructions,
  meant to be delivered turn by turn.

Built to test whether model output quality degrades when a task arrives
sharded across a multi-turn conversation instead of all at once. See
[`SolusOps/sister-benchmark-generations`](https://huggingface.co/datasets/SolusOps/sister-benchmark-generations)
for our own models' outputs on this task set.

## Fields

| field | type | description |
|---|---|---|
| `domain` | string | genre, e.g. `fantasy` |
| `item_id` | int | task index |
| `title` | string | task title |
| `full_instruction` | string | the task as one instruction |
| `shards` | list[string] | the same task split into sequential turns |

## License

This benchmark is licensed under
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
