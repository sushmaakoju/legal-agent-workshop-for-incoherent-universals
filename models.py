"""Symbolic Logic proof method, following proof-sketch-summary.pdf.

Definitions, exactly as in the sketch:
  Domain of discourse D: a non-empty set of abstract
    mathematical objects d1, d2, ...
  If c is a constant, Interpretation I(c) belongs to D.
  If P is a unary predicate, I(P) is a subset of D.
  A mapping function I assigns every constant to an element
  of D and every unary predicate to a subset of D. A rule
  forall x (P(x) -> Q(x)) is true under I iff I(P) subset
  of I(Q). A rule forall x (P(x) -> not Q(x)) is true iff
  I(P) intersect I(Q) is empty.

Correction carried over from the confirmed query: the
sketch's C5 was written as NOT CanFly(Brown_Bat). CanFly
is a premise property, not the query. The negated query
used here is NOT Mammal(Brown_Bat), for query
"Brown bat is a mammal." The PDF's C5 is therefore not
used as the query in this file.

1. The sketch's example interpretation I0 (collapsed KB):
  D = {d1, d2}
  I(Brown_Bat) = d1
  I(Bat) = {d1, d2}      (d1 and d2 are both "bats")
  I(HasWings) = {d1}     (only d1 has wings)
  I(HasBarrel) = {d2}    (only d2 has a barrel)
  Evaluating the four rules the sketch evaluates:
    Rule 1, wings are not barrels:
      I(HasWings) intersect I(HasBarrel) = {d1} intersect
      {d2} = empty  -> TRUE
    Rule 2, bats have wings:
      I(Bat) subset of I(HasWings)? {d1, d2} subset of
      {d1}? No: d2 is a bat but has no wings -> FALSE
    Rule 3, bats have a barrel:
      I(Bat) subset of I(HasBarrel)? {d1, d2} subset of
      {d2}? No: d1 is a bat but has no barrel -> FALSE
    Rule 4, barrels are not wings:
      I(HasBarrel) intersect I(HasWings) = empty -> TRUE
  I0 is therefore NOT a model of the KB: it falsifies
  rules 2 and 3. One failing interpretation alone does not
  prove unsatisfiability; the general proof in (2) does.

2. General proof: no collapsed model exists.
  Suppose, for contradiction, I is a model of the collapsed
  KB. Let d = I(Brown_Bat).
    (a) Bat(Brown_Bat) is a premise, so d in I(Bat).
    (b) Bats have wings: forall x (Bat(x) -> HasWings(x)),
        so d in I(HasWings).
    (c) Bats have a barrel: forall x (Bat(x) -> HasBarrel(x)),
        so d in I(HasBarrel).
    (d) Wings are not barrels: forall x (HasWings(x) ->
        not HasBarrel(x)), so I(HasWings) intersect
        I(HasBarrel) is empty.
  (b) and (c) put d in both sets, contradicting (d).
  Hence no interpretation I satisfies all collapsed rules
  at once. The collapsed KB is unsatisfiable: it has no
  mathematical model. This is the "structural reality of
  incoherence" in the sketch: forcing rules 2 and 3 true
  together breaks rule 1, and vice versa.

3. Two reading models (unresolved level, not collapsed):
  Mammal reading model M_mammal:
    D = {d1}, I(Brown_Bat) = d1,
    I(Bat) = {d1}, I(Mammal) = {d1},
    I(HasWings) = {d1}, I(HasBarrel) = {},
    I(CanFly) = {d1}.  H = Mammal(Brown_Bat) is TRUE.
  Baseball reading model M_baseball:
    D = {d1}, I(Brown_Bat) = d1,
    I(Bat) = {d1}, I(Mammal) = {},
    I(HasWings) = {}, I(HasBarrel) = {d1},
    I(CanFly) = {}.  H is FALSE.
  Each model satisfies its own reading's rules and is
  satisfiable on its own. They disagree on H, so H neither
  follows nor is refuted from the unresolved pair: that is
  "logically inconclusive" at the unresolved level, and
  the NLI label for the pair is Neutral. This is not the
  same as the collapsed "cannot decide" in results_table.py,
  and not the same as step 4's "inconclusive inference".

4. Abstract case (Brown A): replace Bat by A throughout.
  D = {d1, d2}, I(Brown_A) = d1, I(A) = {d1, d2},
  I(HasWings) = {d1}, I(HasBarrel) = {d2}. Evaluations of
  rules 1-4 are identical, and the general proof in (2)
  goes through with A in place of Bat, d = I(Brown_A).
  The mammal / baseball reading models are likewise
  isomorphic, with A in place of Bat. The abstract proof
  is therefore not a new proof: it is the same proof
  under renaming, which is why the Results Table for
  Brown A is identical to Brown Bat.
"""


def pdf_interpretation():
    """The sketch's I0, collapsed, Brown Bat."""
    return {
        "domain": {"d1", "d2"},
        "constants": {"Brown_Bat": "d1"},
        "predicates": {
            "Bat": {"d1", "d2"},
            "HasWings": {"d1"},
            "HasBarrel": {"d2"},
        },
    }


def abstract_pdf_interpretation():
    """I0 with Bat renamed to A, for Brown A."""
    return {
        "domain": {"d1", "d2"},
        "constants": {"Brown_A": "d1"},
        "predicates": {
            "A": {"d1", "d2"},
            "HasWings": {"d1"},
            "HasBarrel": {"d2"},
        },
    }


def evaluate_pdf_rules(interp, keyword="Bat"):
    """Evaluate rules 1-4 of the sketch under an I0-style interp."""
    p = interp["predicates"]
    wings = p["HasWings"]
    barrels = p["HasBarrel"]
    bats = p[keyword]
    return {
        "rule1_wings_not_barrels": not (wings & barrels),
        "rule2_bats_have_wings": bats <= wings,
        "rule3_bats_have_barrel": bats <= barrels,
        "rule4_barrels_not_wings": not (barrels & wings),
    }


def mammal_model():
    return {
        "domain": {"d1"},
        "constants": {"Brown_Bat": "d1"},
        "predicates": {
            "Bat": {"d1"}, "Mammal": {"d1"},
            "HasWings": {"d1"}, "HasBarrel": set(),
            "CanFly": {"d1"},
        },
        "h_true": True,
    }


def baseball_model():
    return {
        "domain": {"d1"},
        "constants": {"Brown_Bat": "d1"},
        "predicates": {
            "Bat": {"d1"}, "Mammal": set(),
            "HasWings": set(), "HasBarrel": {"d1"},
            "CanFly": set(),
        },
        "h_true": False,
    }


def prove_no_collapsed_model():
    """The general proof in (2), as checkable steps."""
    return {
        "assumption": "I is a model of the collapsed KB",
        "steps": [
            "d = I(Brown_Bat); Bat(Brown_Bat) gives d in I(Bat).",
            "Bats have wings gives d in I(HasWings).",
            "Bats have a barrel gives d in I(HasBarrel).",
            "Wings are not barrels gives "
            "I(HasWings) intersect I(HasBarrel) = empty.",
            "d in both sets contradicts the empty intersection.",
        ],
        "conclusion": "No interpretation satisfies the collapsed KB: unsatisfiable.",
    }
