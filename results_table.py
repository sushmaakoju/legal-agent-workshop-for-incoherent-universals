"""Results Table, per the author's proof-sketch steps.

Prerequisite table, per resolution type, per case:
  Columns: NLI Label, Final Label
  Row 1: KB AND NOT QUERY   (entailment test, QUERY = Mammal)
  Row 2: KB AND QUERY       (contradiction test)

Step 1, row labels (a single row alone cannot decide):
  KB AND NOT QUERY:
    empty clause     -> contradiction in refutation, i.e.
                        entailment candidate
    no empty clause  -> neutral or contradiction (undecided
                        from this row alone)
  KB AND QUERY:
    empty clause     -> contradiction candidate
    no empty clause  -> neutral or entailed; this row-level
                        undecided state is called
                        "inconclusive" in step 1. It is NOT
                        the same as step 4's combined
                        "inconclusive inference", and NOT
                        the same as "logically inconclusive"
                        at the unresolved level. See below.

Step 2, combined (both rows together):
  both rows no empty clause -> Neutral

Step 4, combined (both rows together):
  one row empty, the other no empty clause
    -> cannot decide, called "inconclusive inference".
       This is NOT Neutral, and NOT "logically
       inconclusive" (see below).

Both rows empty (not covered by step 4's mixed wording,
so labelled separately, not invented as Neutral):
  both rows empty -> cannot decide, because the collapsed
    KB itself is unsatisfiable: both tests close vacuously
    via the KB-only route, so neither test is query evidence.

Three terms that must not be collapsed:
  Neutral: NLI label (readings disagree), and step 2's
    both-no-empty combined FOL outcome.
  Inconclusive inference: step 4's mixed combined outcome,
    cannot decide from the two resolution tests alone.
  Logically inconclusive: the unresolved-level FOL verdict
    (fol.check_unresolved_worlds): H true in one satisfiable
    world, false in the other, neither H nor not-H follows.
    This is a positive verdict about the unresolved pair,
    not a failure to decide between two tests.

Step 3, Muse calls: see muse_resolution_calls.py. A Muse
call per strategy per test is the recording step; the
deterministic engine in fol.py / resolution_strategies.py
is the cross-check. A Muse result that disagrees with the
deterministic result is an escalation, not a proof, because
Session 2 checks must not trust the model.

Step 5, filled results for this example: see build_table().
Step 6, repeat for: Traditional, Linear, Unit, Input,
Set of Support, Hyper, Ordered (order defined below).

Abstract case (Brown A): the KB is isomorphic to Brown Bat
under renaming Bat -> A (same properties, same disjointness,
same query Mammal). abstract_clauses() performs that
renaming and the same strategies are run on it, so the
Brown A table is a run, not a copy-paste claim. The two
tables come out identical, which is the invariance check
the abstract case is for.
"""

from fol import (
    collapsed_clauses,
    linear_resolve,
    _lit,
)
from resolution_strategies import (
    hyper_resolution,
    input_resolution,
    ordered_resolution,
    set_of_support_resolution,
    unit_resolution,
)
from fol import saturate as traditional_resolution

# Ordered resolution: one order, stated explicitly, as requested.
# Bat > Mammal > HasWings > HasBarrel > CanFly.
ORDER = {"Bat": 5, "Mammal": 4, "HasWings": 3, "HasBarrel": 2, "CanFly": 1}
ABSTRACT_ORDER = {"A": 5, "Mammal": 4, "HasWings": 3, "HasBarrel": 2, "CanFly": 1}


def _linear_any_start(clauses):
    """Linear resolution on a set: any starting clause.

    A linear derivation may start from any clause in the
    set, not only from the query clause, so KB+QUERY closes
    via the Bat route even though a Mammal-started chain
    would not. Reporting only the query-started chain would
    understate what linear resolution on the set derives.
    """
    for start in clauses:
        empty, _chain = linear_resolve(clauses, start, max_depth=6)
        if empty:
            return True
    return False


def abstract_clauses():
    """Collapsed clauses with Bat renamed to A."""
    out = []
    for clause in collapsed_clauses():
        renamed = frozenset(
            ("A" if name == "Bat" else name, negated)
            for name, negated in clause
        )
        out.append(renamed)
    return out


def _strategies_for(is_abstract):
    order = ABSTRACT_ORDER if is_abstract else ORDER

    def ordered(clauses):
        return ordered_resolution(clauses, order)

    def set_of_support(clauses, support):
        return set_of_support_resolution(clauses, support)

    return {
        # saturate returns (bool, steps); take the bool.
        "Traditional": lambda clauses: traditional_resolution(clauses)[0],
        "Linear": _linear_any_start,
        "Unit": unit_resolution,
        "Input": input_resolution,
        "Hyper": hyper_resolution,
        "Ordered": ordered,
    }


def row_label(test, empty):
    """Step 1 row label for one row alone."""
    if test == "kb_and_not_query":
        return (
            "entailment candidate (empty = contradiction)"
            if empty
            else "neutral or contradiction (row alone cannot decide)"
        )
    return (
        "contradiction candidate (empty = contradiction)"
        if empty
        else "neutral or entailed — row-level 'inconclusive' "
        "(row alone cannot decide)"
    )


def combined_label(empty_not_query, empty_query):
    """Steps 2 and 4, plus the both-empty case, labelled separately."""
    if not empty_not_query and not empty_query:
        return "Neutral"
    if empty_not_query != empty_query:
        return "inconclusive inference (cannot decide)"
    return "cannot decide — both empty, collapsed KB unsatisfiable (vacuous)"


def build_table(case_id="brown_bat"):
    """Full Results Table for one case.

    Returns a dict: strategy -> {
      kb_and_not_query: bool, kb_and_query: bool,
      row1_label, row2_label, combined_label,
      nli_label: "Neutral",
    }
    """
    is_abstract = case_id == "brown_a"
    kb = abstract_clauses() if is_abstract else collapsed_clauses()
    not_query = frozenset([_lit("Mammal", True)])
    query = frozenset([_lit("Mammal")])
    strategies = _strategies_for(is_abstract)
    table = {}
    for name, fn in strategies.items():
        if name == "Set of Support":
            continue
        empty_not_q = bool(fn(kb + [not_query]))
        empty_q = bool(fn(kb + [query]))
        table[name] = {
            "kb_and_not_query_empty": empty_not_q,
            "kb_and_query_empty": empty_q,
            "row1_label": row_label("kb_and_not_query", empty_not_q),
            "row2_label": row_label("kb_and_query", empty_q),
            "combined_label": combined_label(empty_not_q, empty_q),
            "nli_label": "Neutral",
        }
    # Set of Support needs its support set, per test.
    empty_not_q = set_of_support_resolution(
        kb + [not_query], [not_query]
    )
    empty_q = set_of_support_resolution(kb + [query], [query])
    table["Set of Support"] = {
        "kb_and_not_query_empty": bool(empty_not_q),
        "kb_and_query_empty": bool(empty_q),
        "row1_label": row_label("kb_and_not_query", empty_not_q),
        "row2_label": row_label("kb_and_query", empty_q),
        "combined_label": combined_label(empty_not_q, empty_q),
        "nli_label": "Neutral",
    }
    # Keep the step-6 order: Traditional, Linear, Unit, Input,
    # Set of Support, Hyper, Ordered.
    order = [
        "Traditional", "Linear", "Unit", "Input",
        "Set of Support", "Hyper", "Ordered",
    ]
    return {name: table[name] for name in order}


def main_output():
    """Generated output, for results_table_output.json."""
    return {
        "brown_bat": build_table("brown_bat"),
        "brown_a": build_table("brown_a"),
        "unresolved": unresolved_table(),
    }


def unresolved_table():
    """The level at which Neutral / logically inconclusive actually sit.

    Unresolved pair: H is true in the mammal world, false in
    the baseball world, neither follows. This is NOT a row of
    the collapsed table above, and it must not be copied from
    a collapsed row.
    """
    return {
        "kb_and_not_query_forces": False,
        "kb_and_query_forces": False,
        "combined_label": "Neutral",
        "fol_verdict": "logically inconclusive",
        "nli_label": "Neutral",
        "scope": "equivocation-induced pairs only",
    }


if __name__ == "__main__":
    import json as _json

    print(_json.dumps(main_output(), indent=1))
