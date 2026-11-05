"""Theory memo rules, adapted from the workshop memo rules.

run_verification(memo, case=None) returns passed plus feedback.
These are structural rules, not a model judgement: a memo must
have both a labelled NLI claim and a FOL claim, must not claim
a signed / only / sequence result its reason does not support,
and must list escalated gaps instead of hiding them.
"""

_OVERCLAIM_PHRASES = (
    "signed statement",
    "only confirmation",
    "sequence established",
    "single model satisfies",
)


def run_verification(memo, case=None):
    problems = []
    if not memo.get("nli_label"):
        problems.append("memo is missing nli_label.")
    if not memo.get("fol_claim"):
        problems.append("memo is missing fol_claim.")
    reason = " ".join(
        str(memo.get(key, "")) for key in ("nli_reason", "fol_reason")
    ).lower()
    # An overclaim phrase is refused unless the memo explicitly
    # marks that finding as escalated, not proven.
    escalated = "escalated" in reason or memo.get("escalated")
    for phrase in _OVERCLAIM_PHRASES:
        if phrase in reason and not escalated:
            problems.append(
                f"memo claims '{phrase}' without marking it as "
                "escalated: narrow the claim to what is cited, "
                "or escalate it as a gap for the reviewer."
            )
    if problems:
        return {"passed": False, "feedback": " ".join(problems), "score": 0}
    return {
        "passed": True,
        "feedback": "Memo passes the structural memo rules.",
        "score": 1,
    }
