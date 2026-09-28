#!/usr/bin/env python3
"""Stage 5d: upload release/ to Hugging Face Hub.

**DO NOT RUN THIS FROM AN AUTOMATED/UNATTENDED SESSION.** Per the task
brief's NETWORK RULES and GOAL, uploading is done by hand, by one of the
authors, using their own Hugging Face credentials. This script exists so
that when the authors are ready, the actual upload command is a single
reviewed, deliberate action rather than something improvised at the
terminal. See docs/UPLOAD_GUIDE.md for the full manual walkthrough.

Usage (run manually, by an author, after `export HF_TOKEN=...`):
    python3 scripts/upload_to_hf.py --repo-id <username-or-org>/<dataset-name>
        [--release-dir release] [--private]

Requires the `huggingface_hub` package (`pip install huggingface_hub`) —
not installed by default in this pipeline, since it is never invoked
automatically. Reads the token ONLY from the HF_TOKEN environment
variable; never pass a token on the command line (it would end up in
shell history).
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base = Path(__file__).resolve().parent.parent
    parser.add_argument("--repo-id", required=True,
                         help="Hugging Face dataset repo id, e.g. 'amosnabasa/luganda-yoruba-short-text'")
    parser.add_argument("--release-dir", type=Path, default=base / "release")
    parser.add_argument("--private", action="store_true", help="Create/update the repo as private.")
    parser.add_argument("--commit-message", default="Upload dataset release")
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN environment variable is not set. "
              "Set it (e.g. `export HF_TOKEN=hf_...`) and re-run. "
              "Never pass a token as a command-line argument.", file=sys.stderr)
        return 1

    if not args.release_dir.exists() or not any(args.release_dir.iterdir()):
        print(f"ERROR: {args.release_dir} is empty or missing. Run scripts/build_release.py first.",
              file=sys.stderr)
        return 1

    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("ERROR: huggingface_hub is not installed. Run: pip install huggingface_hub",
              file=sys.stderr)
        return 1

    api = HfApi(token=token)
    print(f"About to create/update dataset repo '{args.repo_id}' "
          f"({'private' if args.private else 'public'}) from '{args.release_dir}'.")
    print("This is a real, live upload. Press Ctrl+C now to cancel.")

    api.create_repo(repo_id=args.repo_id, repo_type="dataset", private=args.private, exist_ok=True)
    api.upload_folder(
        repo_id=args.repo_id,
        repo_type="dataset",
        folder_path=str(args.release_dir),
        commit_message=args.commit_message,
    )
    print(f"Uploaded {args.release_dir} -> https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
