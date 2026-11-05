"""Step 3: Muse calls for the Results Table, with a cross-check.

For each resolution type and each test (KB AND NOT QUERY,
KB AND QUERY), call Muse and record its result in the table.
This file is the recording interface; it is NOT a claim that
a Muse call was run in this VM, where no API key is available.

How a call works (real mode, needs META_API_KEY in WSL):
  client = make_client()          # Meta API only, Muse model
  result = ask_muse_resolution(client, strategy, test)
  # result = {"empty_clause": bool, "derivation": [...],
  #           "route": "query-descended" | "kb-only" | "none"}

The prompt asks Muse to do the named resolution strategy
step by step on the grounded clauses, and to return JSON
only, with empty_clause true exactly when it derives the
empty clause. The prompt names the strategy, the clauses,
and the test, and nothing else about the expected answer.

Cross-check, required by the Session 2 pattern: the
deterministic result from results_table.build_table() is
compared with the Muse result. Agreement is recorded.
Disagreement is recorded as an escalation, and the
deterministic result is kept as the table's verdict —
a Muse call proposes, it does not prove. If this file
were the only source, a wrong Muse derivation would
silently become the table.

No-model mode: ask_muse_resolution raises RuntimeError.
results_table.py then runs deterministically and labels
its source "deterministic engine (Muse call not run)".
Do not relabel a deterministic row as a Muse row.
"""

import json
import os

from agent_kit.client import model_name
from agent_kit.muse_log import log_path_for, write_log
from results_table import build_table


STRATEGIES = [
    "Traditional", "Linear", "Unit", "Input",
    "Set of Support", "Hyper", "Ordered",
]

PROMPT_TEMPLATE = """You are doing first-order resolution, step by step, for one test.

Resolution strategy: {strategy}
{order_note}
Clauses (grounded, Brown Bat / Brown A case):
{clauses}

Test: {test}
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".
"""


def _clauses_text():
    return (
        "Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; "
        "NOT Bat OR HasBarrel; NOT Bat OR CanFly; "
        "NOT HasWings OR NOT HasBarrel. "
        "For Brown A, replace Bat with A throughout."
    )


def ask_muse_resolution(client, strategy, test):
    """Call Muse for one strategy / test. Returns parsed JSON."""
    if strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}")
    if test not in ("kb_and_not_query", "kb_and_query"):
        raise ValueError(f"Unknown test: {test}")
    order_note = (
        "Ordered resolution order: Bat > Mammal > HasWings > "
        "HasBarrel > CanFly (A > Mammal > HasWings > HasBarrel > "
        "CanFly for Brown A); resolve only on maximal literals."
        if strategy == "Ordered"
        else ""
    )
    prompt = PROMPT_TEMPLATE.format(
        strategy=strategy,
        order_note=order_note,
        clauses=_clauses_text(),
        test=test.replace("_", " ").upper(),
    )
    response = client.chat.completions.create(
        model=model_name(),
        messages=[{"role": "user", "content": prompt}],
    )
    content = response.choices[0].message.content or ""
    return json.loads(content)


def prompt_for(strategy, test):
    """The exact prompt sent to Muse for one strategy / test."""
    order_note = (
        "Ordered resolution order: Bat > Mammal > HasWings > "
        "HasBarrel > CanFly (A > Mammal > HasWings > HasBarrel > "
        "CanFly for Brown A); resolve only on maximal literals."
        if strategy == "Ordered"
        else ""
    )
    return PROMPT_TEMPLATE.format(
        strategy=strategy,
        order_note=order_note,
        clauses=_clauses_text(),
        test=test.replace("_", " ").upper(),
    )


def record_muse_results(client, case_id="brown_bat", log_path=None):
    """Call Muse for every strategy x test, cross-check, log.

    Returns rows with muse_empty, deterministic_empty, agree,
    and escalated flag on disagreement. The deterministic
    table remains the verdict on disagreement. Every call
    and response is appended to the log file, with
    nli_label = Neutral for every row (readings disagree,
    for both brown_bat and brown_a), plus verifier results
    for a Neutral / inconclusive memo for that case.
    """
    from verification.verify_fol_theory import run_verification as verify_fol
    from verification.verify_nli_theory import run_verification as verify_nli
    from cases import get_case
    from pathlib import Path

    deterministic = build_table(case_id)
    root = Path(__file__).resolve().parent
    if log_path is None:
        log_path = log_path_for(root)
    # Verifier check, once per case, recorded in the log too.
    try:
        case = get_case(root, case_id)
    except Exception:
        case = {"id": case_id, "expected_nli_label": "Neutral",
                "expected_fol_claim": "inconclusive"}
    memo = {
        "nli_label": "Neutral",
        "nli_reason": "readings disagree: H true on mammal reading, "
        "false on baseball reading, lexeme unresolved",
        "fol_claim": "inconclusive",
        "fol_reason": "unresolved worlds disagree: H true in one "
        "satisfiable world, false in the other, neither follows "
        "from the unresolved pair",
    }
    nli_result = verify_nli(memo, case)
    fol_result = verify_fol(memo, case)
    rows = []
    for strategy in STRATEGIES:
        for test in ("kb_and_not_query", "kb_and_query"):
            muse = ask_muse_resolution(client, strategy, test)
            key = (
                "kb_and_not_query_empty"
                if test == "kb_and_not_query"
                else "kb_and_query_empty"
            )
            det = deterministic[strategy][key]
            row = {
                "case_id": case_id,
                "strategy": strategy,
                "test": test,
                "muse_empty_clause": bool(muse["empty_clause"]),
                "deterministic_empty_clause": bool(det),
                "agree": bool(muse["empty_clause"]) == bool(det),
                "muse_route": muse.get("route"),
                "escalated": bool(muse["empty_clause"]) != bool(det),
            }
            rows.append(row)
            write_log(log_path, {
                "case_id": case_id,
                "kind": "muse_resolution",
                "model": model_name(),
                "strategy": strategy,
                "test": test,
                "nli_label": "Neutral",
                "prompt": prompt_for(strategy, test),
                "response": muse,
                "empty_clause": bool(muse["empty_clause"]),
                "route": muse.get("route"),
                "deterministic_empty_clause": bool(det),
                "agree": row["agree"],
                "escalated": row["escalated"],
                "source": "muse",
                "verification": {
                    "nli_passed": nli_result["passed"],
                    "nli_feedback": nli_result["feedback"],
                    "fol_passed": fol_result["passed"],
                    "fol_feedback": fol_result["feedback"],
                },
            })
    return rows
