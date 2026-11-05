"""Run progress: save and load a run, one JSON file per run.

Progress lives under <root>/workspace/<run_id>.json. It is
runtime state, not source, and it is git-ignored. Saving after
every turn is what makes resume_run possible: a run that stops
at the turn limit, or at a reviewer handoff, is not lost.
"""

from __future__ import annotations

import json
from pathlib import Path


def workspace_dir(root: Path) -> Path:
    path = Path(root) / "workspace"
    path.mkdir(parents=True, exist_ok=True)
    return path


def progress_path(root: Path, run_id: str) -> Path:
    return workspace_dir(root) / f"{run_id}.json"


def save_progress(root: Path, progress: dict) -> Path:
    path = progress_path(root, progress["run_id"])
    # Write to a temp file, then replace, so a crash mid-write
    # does not leave a half-written progress file.
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(progress, indent=2, sort_keys=True))
    tmp.replace(path)
    return path


def load_progress(root: Path, run_id: str) -> dict:
    path = progress_path(root, run_id)
    if not path.is_file():
        raise FileNotFoundError(f"no run found: {run_id} (looked in {path})")
    return json.loads(path.read_text())
