"""Tools the model may call. Tools sit inside the loop, not
as model-chosen verifiers: the model chooses *which* tool to
call and when, but the tools themselves, and the verifiers
they call, are fixed code and do not trust the model.

Tool results returned to the model contain passed + feedback
only. Scores and escalated-gap lists are reviewer-facing and
are kept in the run progress, not in tool results.

Tools (all take JSON arguments):
- list_cases: list available case ids
- read_case(case_id): premise and hypothesis for one case
- check_nli(case_id, nli_label, nli_reason): NLI theory check
- check_fol(case_id, fol_claim, fol_reason): FOL theory check
- submit_memo(case_id, memo): run all verifiers; on pass the
  memo is filed, on refusal the feedback is returned
- escalate(case_id, finding, reason): record an escalation
  for a finding that cannot be proven, and stop guessing
"""

from __future__ import annotations

import json
from pathlib import Path

from cases import get_case, load_cases
from verification.verify_fol_theory import run_verification as verify_fol
from verification.verify_memo import run_verification as verify_memo
from verification.verify_nli_theory import run_verification as verify_nli


def _strip(result: dict) -> dict:
    return {"passed": result["passed"], "feedback": result["feedback"]}


def _run_all_verifiers(root: Path, case: dict, memo: dict) -> dict:
    results = {
        "memo_rules": verify_memo(memo, case),
        "nli": verify_nli(memo, case),
        "fol": verify_fol(memo, case),
    }
    passed = all(r["passed"] for r in results.values())
    feedback = " ".join(
        r["feedback"] for r in results.values() if not r["passed"]
    ) or "All verifiers passed."
    escalated = []
    for r in results.values():
        escalated.extend(r.get("escalated_gaps", []))
    return {
        "passed": passed,
        "feedback": feedback,
        "results": results,
        "escalated_gaps": sorted(set(escalated)),
    }


def run_tool(root: Path, name: str, arguments: dict, progress: dict) -> dict:
    """Execute one tool call. Returns the result for the model."""
    if name == "list_cases":
        return {
            "passed": True,
            "feedback": "",
            "cases": [c["id"] for c in load_cases(root)],
        }
    if name == "read_case":
        case = get_case(root, arguments["case_id"])
        return {
            "passed": True,
            "feedback": "",
            "case": {
                "id": case["id"],
                "premise": case["premise"],
                "hypothesis": case["hypothesis"],
            },
        }
    if name == "check_nli":
        case = get_case(root, arguments["case_id"])
        memo = {
            "nli_label": arguments.get("nli_label", ""),
            "nli_reason": arguments.get("nli_reason", ""),
        }
        return _strip(verify_nli(memo, case))
    if name == "check_fol":
        case = get_case(root, arguments["case_id"])
        memo = {
            "fol_claim": arguments.get("fol_claim", ""),
            "fol_reason": arguments.get("fol_reason", ""),
        }
        return _strip(verify_fol(memo, case))
    if name == "submit_memo":
        case = get_case(root, arguments["case_id"])
        memo = arguments.get("memo", {})
        if isinstance(memo, str):
            memo = json.loads(memo)
        checked = _run_all_verifiers(root, case, memo)
        if checked["passed"]:
            progress["memo"] = memo
            progress["case_id"] = case["id"]
            progress["escalated_gaps"] = checked["escalated_gaps"]
            return {
                "passed": True,
                "feedback": "Memo filed and passed all verifiers.",
                "status": "answered",
            }
        return {
            "passed": False,
            "feedback": checked["feedback"],
            "status": "refused",
        }
    if name == "escalate":
        progress.setdefault("escalations", []).append(
            {
                "case_id": arguments.get("case_id"),
                "finding": arguments.get("finding"),
                "reason": arguments.get("reason"),
            }
        )
        return {
            "passed": True,
            "feedback": "Escalation recorded. Stop guessing on this finding.",
            "status": "escalated",
        }
    raise ValueError(f"unknown tool: {name}")


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_cases",
            "description": "List available theory case ids.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_case",
            "description": "Read the premise and hypothesis for one case.",
            "parameters": {
                "type": "object",
                "properties": {"case_id": {"type": "string"}},
                "required": ["case_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_nli",
            "description": "Check an NLI label claim against the readings check.",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "nli_label": {"type": "string"},
                    "nli_reason": {"type": "string"},
                },
                "required": ["case_id", "nli_label", "nli_reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_fol",
            "description": "Check a FOL claim against the resolution check.",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "fol_claim": {"type": "string"},
                    "fol_reason": {"type": "string"},
                },
                "required": ["case_id", "fol_claim", "fol_reason"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "submit_memo",
            "description": "File a theory memo. It is checked by all verifiers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "memo": {"type": "object"},
                },
                "required": ["case_id", "memo"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate",
            "description": "Escalate a finding that cannot be proven, instead of guessing.",
            "parameters": {
                "type": "object",
                "properties": {
                    "case_id": {"type": "string"},
                    "finding": {"type": "string"},
                    "reason": {"type": "string"},
                },
                "required": ["case_id", "finding", "reason"],
            },
        },
    },
]
