"""
Push the collected baseline generations to their own Hugging Face dataset
repo, one split per model. Run this independently of push_benchmark.py --
this repo's history is about new experiment runs, not benchmark versions.

Setup:
    pip install datasets huggingface_hub
    huggingface-cli login          # or: export HF_TOKEN=hf_xxx

Usage (run from the repo root):
    python runs/hf_upload/push_generations.py \\
        --repo-id YOUR_USERNAME/sister-benchmark-generations

    # public instead of the default private:
    python runs/hf_upload/push_generations.py \\
        --repo-id YOUR_USERNAME/sister-benchmark-generations --public

What gets pushed:
    - each runs/results/results_<model>.jsonl -> its own split
      (e.g. "qwen_qwen3_5_9b", "llama_3_1_8b_instruct", ...)
    - runs/results/all_results.jsonl is NOT re-pushed -- it's just the
      concatenation of those splits (duplicating it would double storage
      for nothing). Reconstruct it after loading if you ever need it:
          from datasets import load_dataset, concatenate_datasets
          gens = load_dataset(repo_id)
          all_rows = concatenate_datasets(list(gens.values()))
    - runs/results/index.json -> uploaded as a plain repo file
      (generations_index.json), NOT a dataset split -- it's run
      provenance/integrity metadata (which benchmark version, hashes,
      progress), not row-shaped data.
"""

import argparse
import glob
import os
import re

from datasets import Dataset, DatasetDict
from huggingface_hub import HfApi


def split_name_for(path: str) -> str:
    stem = os.path.basename(path)
    stem = re.sub(r"^results_", "", stem)
    stem = re.sub(r"\.jsonl$", "", stem)
    return re.sub(r"[^0-9a-zA-Z]+", "_", stem).strip("_")


def load_generations_by_model(results_dir: str) -> DatasetDict:
    files = sorted(glob.glob(os.path.join(results_dir, "results_*.jsonl")))
    if not files:
        raise SystemExit(f"No results_*.jsonl files found under {results_dir}")
    splits = {}
    for path in files:
        name = split_name_for(path)
        splits[name] = Dataset.from_json(path)
        print(f"  split '{name}': {len(splits[name])} rows  ({os.path.basename(path)})")
    return DatasetDict(splits)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-id", required=True, help="e.g. your-username/sister-benchmark-generations")
    ap.add_argument("--results-dir", default="runs/results")
    ap.add_argument("--public", dest="private", action="store_false", default=True,
                     help="Push as a public repo instead of the default private repo.")
    args = ap.parse_args()

    print(f"Loading per-model generations from {args.results_dir}/results_*.jsonl ...")
    generations = load_generations_by_model(args.results_dir)

    visibility = "private" if args.private else "PUBLIC"
    print(f"Pushing to {args.repo_id} ({visibility}) ...")
    generations.push_to_hub(args.repo_id, private=args.private)

    index_path = os.path.join(args.results_dir, "index.json")
    if os.path.exists(index_path):
        print("Uploading run provenance/index file (not a dataset split) ...")
        HfApi().upload_file(
            path_or_fileobj=index_path,
            path_in_repo="generations_index.json",
            repo_id=args.repo_id,
            repo_type="dataset",
        )

    print(f"\nDone: https://huggingface.co/datasets/{args.repo_id}")
    print("Now: paste runs/hf_upload/DATASET_CARD_generations.md content into the repo's README.")


if __name__ == "__main__":
    main()
