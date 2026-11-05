"""Case loading for the theory workshop.

Loads cases/*.json (Brown Bat, Brown A, and any future case
files with the same fields), plus, if present,
cases/dataset/combined.jsonl (one JSON object per line, with
at least id, premise, hypothesis). The combined.jsonl file is
not included in this project; see DATASET.md.
"""

from __future__ import annotations

import json
from pathlib import Path


def load_cases(root: Path) -> list[dict]:
    cases_dir = Path(root) / "cases"
    cases: list[dict] = []
    seen: set[str] = set()
    if cases_dir.is_dir():
        for path in sorted(cases_dir.glob("*.json")):
            if path.name == "dataset_schema.json":
                continue
            with path.open() as f:
                case = json.load(f)
            case.setdefault("id", path.stem)
            if case["id"] not in seen:
                seen.add(case["id"])
                cases.append(case)
        dataset_file = cases_dir / "dataset" / "combined.jsonl"
        if dataset_file.is_file():
            with dataset_file.open() as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    case = json.loads(line)
                    if case.get("id") not in seen:
                        seen.add(case["id"])
                        cases.append(case)
    return cases


def get_case(root: Path, case_id: str) -> dict:
    for case in load_cases(root):
        if case["id"] == case_id:
            return case
    raise KeyError(f"unknown case: {case_id}")
