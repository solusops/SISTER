"""
Push the consolidated study dataset to one Hugging Face dataset repo, as six
independent configs (browsable separately on the Hub, one repo URL to cite).

This supersedes push_benchmark.py + push_generations.py for NEW pushes. Those
two scripts and the two repos they built (sister-benchmark,
sister-benchmark-generations) are left untouched as legacy -- still accurate,
just narrower in scope than this repo's job now that the evaluation/judging
work exists too.

Setup:
    pip install datasets huggingface_hub
    huggingface-cli login          # or: export HF_TOKEN=hf_xxx

Usage (run from the repo root):
    python runs/hf_upload/push_dataset.py --repo-id YOUR_USERNAME/REPO_NAME

    # only push some configs while iterating:
    python runs/hf_upload/push_dataset.py --repo-id YOUR_USERNAME/REPO_NAME \\
        --configs benchmark,pointwise_scores

    # public instead of the default private:
    python runs/hf_upload/push_dataset.py --repo-id YOUR_USERNAME/REPO_NAME --public

Configs pushed (each is its own DatasetDict via push_to_hub(..., config_name=...)):
    benchmark                   -- split "tasks"                (runs/benchmark_data.json)
    generations                 -- one split per model           (runs/results/results_*.jsonl)
    pointwise_scores            -- split "scores"                (evaluations/scores.jsonl)
    pairwise_validation         -- splits "primary", "reversed"  (human_validation/model_pairwise_*.jsonl)
    evidence_first_validation   -- splits "primary", "reversed"  (human_validation/evidence_first_*.jsonl)
    human_eval_sample            -- one HF config, sample_30.jsonl (different schema from annotations, so a
    human_eval_annotations       -- separate config, not a second split -- see push_human_eval())

Plain repo files pushed alongside (NOT dataset splits -- provenance, schemas,
and methodology docs are not row-shaped data; forcing them into splits would
make them look like records of a dataset they aren't):
    benchmark/constraints.jsonl
    benchmark/constraint_schema.json
    evaluations/judge_config.json
    generations/generations_index.json      (from runs/results/index.json)
    methodology/methodology_results.md
    methodology/evidence_first_methodology.md
    methodology/position_consistency_summary.json
    methodology/evidence_first_position_consistency.json
    methodology/evidence_first_constraint_stability.json
    methodology/evidence_first_dimension_stability.json
    ARTIFACT_MANIFEST.json                  (if present at repo root -- see tools/build_manifest.py)

Deliberately NOT pushed here (kept in Git for provenance, not published as
dataset rows -- see the plan this script was built from):
    native_judge_batches/, native_judge_long_batches/, native_judge_repair_batches/
    (the exact judge prompts -- Git-only)
    scores_auto.jsonl (superseded by evaluations/scores.jsonl)
    qc_review_36.md, excluded_for_manual_annotation.jsonl
    runs/results/all_results.jsonl (redundant concat of the generations splits)
"""

import argparse
import glob
import json
import os
import re

from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi

ALL_CONFIGS = [
    "benchmark",
    "generations",
    "pointwise_scores",
    "pairwise_validation",
    "evidence_first_validation",
    "human_eval",
]

PLAIN_FILES = [
    ("evaluations/constraints.jsonl", "benchmark/constraints.jsonl"),
    ("evaluations/constraint_schema.json", "benchmark/constraint_schema.json"),
    ("evaluations/judge_config.json", "evaluations/judge_config.json"),
    ("runs/results/index.json", "generations/generations_index.json"),
    ("evaluations/human_validation/methodology_results.md", "methodology/methodology_results.md"),
    ("evaluations/human_validation/evidence_first_methodology.md", "methodology/evidence_first_methodology.md"),
    ("evaluations/human_validation/position_consistency_summary.json", "methodology/position_consistency_summary.json"),
    ("evaluations/human_validation/evidence_first_position_consistency.json", "methodology/evidence_first_position_consistency.json"),
    ("evaluations/human_validation/evidence_first_constraint_stability.json", "methodology/evidence_first_constraint_stability.json"),
    ("evaluations/human_validation/evidence_first_dimension_stability.json", "methodology/evidence_first_dimension_stability.json"),
    ("evaluations/human_validation/human_model_agreement_summary.json", "methodology/human_model_agreement_summary.json"),
    ("evaluations/human_validation/human_model_disagreements.md", "methodology/human_model_disagreements.md"),
    ("ARTIFACT_MANIFEST.json", "ARTIFACT_MANIFEST.json"),
]


def split_name_for(path: str) -> str:
    stem = os.path.basename(path)
    stem = re.sub(r"^results_", "", stem)
    stem = re.sub(r"\.jsonl$", "", stem)
    return re.sub(r"[^0-9a-zA-Z]+", "_", stem).strip("_")


def push_benchmark(repo_id: str, private: bool) -> None:
    with open("runs/benchmark_data.json", encoding="utf-8") as f:
        tasks = Dataset.from_list(json.load(f))
    print(f"  benchmark/tasks: {len(tasks)} rows")
    DatasetDict({"tasks": tasks}).push_to_hub(repo_id, config_name="benchmark", private=private)


def push_generations(repo_id: str, private: bool) -> None:
    files = sorted(glob.glob(os.path.join("runs", "results", "results_*.jsonl")))
    if not files:
        raise SystemExit("No runs/results/results_*.jsonl files found")
    splits = {}
    for path in files:
        name = split_name_for(path)
        splits[name] = Dataset.from_json(path)
        print(f"  generations/{name}: {len(splits[name])} rows")
    DatasetDict(splits).push_to_hub(repo_id, config_name="generations", private=private)


def push_pointwise_scores(repo_id: str, private: bool) -> None:
    scores = Dataset.from_json("evaluations/scores.jsonl")
    print(f"  pointwise_scores/scores: {len(scores)} rows")
    DatasetDict({"scores": scores}).push_to_hub(repo_id, config_name="pointwise_scores", private=private)


def push_pairwise_validation(repo_id: str, private: bool) -> None:
    base = "evaluations/human_validation"
    primary = Dataset.from_json(f"{base}/model_pairwise_primary.jsonl")
    reversed_ = Dataset.from_json(f"{base}/model_pairwise_reversed.jsonl")
    print(f"  pairwise_validation/primary: {len(primary)} rows, reversed: {len(reversed_)} rows")
    DatasetDict({"primary": primary, "reversed": reversed_}).push_to_hub(
        repo_id, config_name="pairwise_validation", private=private
    )


def push_evidence_first_validation(repo_id: str, private: bool) -> None:
    base = "evaluations/human_validation"
    primary = Dataset.from_json(f"{base}/evidence_first_primary.jsonl")
    reversed_ = Dataset.from_json(f"{base}/evidence_first_reversed.jsonl")
    print(f"  evidence_first_validation/primary: {len(primary)} rows, reversed: {len(reversed_)} rows")
    DatasetDict({"primary": primary, "reversed": reversed_}).push_to_hub(
        repo_id, config_name="evidence_first_validation", private=private
    )


def push_human_eval(repo_id: str, private: bool) -> None:
    # sample_30.jsonl and annotations.jsonl have genuinely different schemas
    # (task/response fields vs. annotator judgment fields) -- datasets'
    # DatasetDict.push_to_hub requires identical features across the splits
    # of one config, so these are two configs, not two splits of one.
    base = "evaluations/human_validation"
    sample = Dataset.from_json(f"{base}/sample_30.jsonl")
    annotations = Dataset.from_json(f"{base}/annotations.jsonl")
    print(f"  human_eval_sample: {len(sample)} rows, human_eval_annotations: {len(annotations)} rows")
    DatasetDict({"sample": sample}).push_to_hub(repo_id, config_name="human_eval_sample", private=private)
    DatasetDict({"annotations": annotations}).push_to_hub(repo_id, config_name="human_eval_annotations", private=private)


CONFIG_PUSHERS = {
    "benchmark": push_benchmark,
    "generations": push_generations,
    "pointwise_scores": push_pointwise_scores,
    "pairwise_validation": push_pairwise_validation,
    "evidence_first_validation": push_evidence_first_validation,
    "human_eval": push_human_eval,
}


def push_plain_files(repo_id: str) -> None:
    api = HfApi()
    for local_path, repo_path in PLAIN_FILES:
        if not os.path.exists(local_path):
            print(f"  (skip, not found) {local_path}")
            continue
        print(f"  {local_path} -> {repo_path}")
        api.upload_file(
            path_or_fileobj=local_path,
            path_in_repo=repo_path,
            repo_id=repo_id,
            repo_type="dataset",
        )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-id", required=True, help="e.g. your-username/incremental-instruction-creative-writing")
    ap.add_argument("--configs", default=",".join(ALL_CONFIGS),
                     help="comma-separated subset of: " + ",".join(ALL_CONFIGS))
    ap.add_argument("--skip-plain-files", action="store_true",
                     help="skip the non-split repo files (schemas, methodology docs, manifest)")
    ap.add_argument("--public", dest="private", action="store_false", default=True,
                     help="push as a public repo instead of the default private repo")
    args = ap.parse_args()

    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    unknown = set(configs) - set(ALL_CONFIGS)
    if unknown:
        raise SystemExit(f"Unknown config(s): {sorted(unknown)}; choose from {ALL_CONFIGS}")

    visibility = "private" if args.private else "PUBLIC"
    print(f"Pushing to {args.repo_id} ({visibility}) -- configs: {configs}")
    for name in configs:
        print(f"Config: {name}")
        CONFIG_PUSHERS[name](args.repo_id, args.private)

    if not args.skip_plain_files:
        print("Plain repo files:")
        push_plain_files(args.repo_id)

    print(f"\nDone: https://huggingface.co/datasets/{args.repo_id}")
    print("Now: paste runs/hf_upload/DATASET_CARD.md content into the repo's README,")
    print("then note the exact commit/revision this push corresponds to before citing it.")


if __name__ == "__main__":
    main()
