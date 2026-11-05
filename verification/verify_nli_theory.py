"""NLI theory verifier. Follows the workshop Session 2 contract.

run_verification(memo, case=None) returns passed plus feedback.
The agent sees only the feedback. Any score is reviewer-facing
only and must be stripped before it reaches the agent.
"""

from nli import nli_label

# Verify means: check against the Results Table proof.
# The table's NLI Label is Neutral for every strategy and
# both cases (Brown Bat and Brown A); see results_table.py.
try:
    from results_table import build_table
except ImportError:  # pragma: no cover
    build_table = None


def run_verification(memo, case=None):
    """Check a theory memo's NLI claim against the readings check.

    memo is a dict with, at least, "nli_label" and "nli_reason".
    If case gives expected_nli_label, the memo must match it;
    otherwise the equivocation-induced expectation is Neutral.
    """
    expected_label = None
    if case:
        expected_label = case.get("expected_nli_label")
    if not expected_label and build_table is not None:
        # Results Table NLI Label, for this case, all strategies.
        case_id = case.get("id") if case else "brown_bat"
        table = build_table(case_id)
        expected_label = table["Traditional"]["nli_label"]
    if not expected_label:
        expected_label = nli_label()["label"]

    claimed = (memo.get("nli_label") or "").strip()
    reason = (memo.get("nli_reason") or "").lower()

    problems = []
    if claimed != expected_label:
        problems.append(
            "nli_label is not supported by its readings: "
            "mammal reading gives H true, baseball reading gives "
            "H false, so neither Entailment nor Contradiction is "
            "forced for the unresolved pair."
        )
    if claimed == "Neutral" and "reading" not in reason and "disagree" not in reason:
        problems.append(
            "Neutral claim gives no readings-disagreement reason: "
            "state that H is true on one reading and false on the "
            "other, and that the lexeme is not disambiguated."
        )

    if problems:
        return {"passed": False, "feedback": " ".join(problems), "score": 0}
    return {
        "passed": True,
        "feedback": "NLI label matches the readings check.",
        "score": 1,
    }
