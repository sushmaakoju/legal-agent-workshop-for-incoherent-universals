"""FOL theory verifier. Follows the workshop Session 2 contract.

run_verification(memo, case=None) returns passed plus feedback.
The agent sees only the feedback. Any score is reviewer-facing
only and must be stripped before it reaches the agent.
"""

from fol import fol_verdict

# Verify means: check against THIS proof, the Results Table.
# results_table.build_table() is the proof to verify against:
# collapsed combined labels are all "cannot decide" (both
# empty) except Set of Support, which is "inconclusive
# inference". A memo claiming entailed / contradicted from
# collapsed resolution therefore fails against the table,
# not just against fol_verdict() alone.
try:
    from results_table import build_table
except ImportError:  # pragma: no cover - direct module run
    build_table = None


def run_verification(memo, case=None):
    """Check a theory memo's FOL claim against the Results Table."""
    verdict = fol_verdict()
    table = None
    if build_table is not None:
        case_id = case.get("id") if case else None
        table = build_table(case_id or "brown_bat")
    expected = None
    if case:
        expected = case.get("expected_fol_claim")
    if not expected:
        expected = "inconclusive"

    claim = (memo.get("fol_claim") or "").strip().lower()
    reason = (memo.get("fol_reason") or "").lower()

    problems = []

    if claim in ("entailed", "contradicted"):
        problems.append(
            "fol_claim is not supported against the Results "
            "Table (results_table.py / RESULTS_TABLE.md): "
            "every collapsed strategy gives cannot decide "
            "(both empty, KB unsatisfiable) except Set of "
            "Support, which gives inconclusive inference. "
            "A collapsed empty clause alone, via wings / "
            "barrel without using the query, does not prove "
            "entailment or contradiction."
        )
    if claim != expected:
        problems.append(
            "fol_claim does not match the expected claim for "
            "this equivocation-induced case."
        )
    if "single model" in reason or "satisfies the collapsed" in reason:
        problems.append(
            "Collapsed KB has no model: no interpretation gives "
            "one individual both wings and a barrel while wings "
            "exclude barrels. Report this as a gap, do not claim "
            "a satisfying model for the collapsed KB."
        )
    if claim == "inconclusive" and "world" not in reason and "unresolved" not in reason:
        problems.append(
            "Inconclusive claim gives no unresolved-worlds "
            "reason: state that H is true in one satisfiable "
            "world and false in the other, and that neither "
            "follows from the unresolved pair."
        )
    if claim not in ("inconclusive", "entailed", "contradicted"):
        problems.append(
            "fol_claim must be one of inconclusive, entailed, "
            "contradicted, so the check can test it."
        )

    if problems:
        return {
            "passed": False,
            "feedback": " ".join(problems),
            "score": 0,
            "escalated_gaps": ["collapsed_model_unsatisfiable"]
            if verdict["collapsed_model_gap"]
            else [],
        }
    return {
        "passed": True,
        "feedback": "FOL claim inconclusive matches the unresolved-worlds check.",
        "score": 1,
        "escalated_gaps": ["collapsed_model_unsatisfiable"],
    }
