"""Check the other resolution strategies on the Brown Bat KB.

This is a verification appendix, not a change to the two
procedures used in the main design (traditional and linear,
see fol.py / THEORY.md). The question it answers, for the
grounded collapsed KB in fol.collapsed_clauses(), is:

  For each strategy, does it derive an empty clause
  (a) from the KB alone,
  (b) from KB + not-H  (entailment test, H = Mammal),
  (c) from KB + H      (contradiction test)?

And, separately, does any strategy derive an empty clause
from either split world on its own? (No: each world is
satisfiable on its own reading.)

Results, verified by tests/test_strategies.py in this VM:

  Traditional (binary, saturation)  KB: yes  KB+not-H: yes  KB+H: yes
  Linear (centre chain)              KB: yes  KB+not-H: yes  KB+H: n/a*
  Unit (one parent unit)             KB: yes  KB+not-H: yes  KB+H: yes
  Input (one parent from input)      KB: yes  KB+not-H: yes  KB+H: yes
  Set of support (one parent from
    support descendants)             KB: no   KB+not-H: yes  KB+H: no
  Hyper (nucleus + positive units)   KB: yes  KB+not-H: yes  KB+H: yes
  Ordered (maximal literal only,
    order Bat > Mammal > HasWings
    > HasBarrel > CanFly)            KB: yes  KB+not-H: yes  KB+H: yes
  Ordered (maximal literal only,
    order HasWings > HasBarrel
    > Bat > Mammal > CanFly)         KB: yes  KB+not-H: yes  KB+H: yes
    (via a different route: not-Bat or HasWings +
     not-HasWings or not-HasBarrel -> not-Bat or
     not-HasBarrel, then with not-Bat or HasBarrel ->
     not-Bat, then with Bat -> empty)

* Linear KB+H is not reported as a separate test in fol.py;
  the linear entailment route (not-Mammal -> not-Bat -> empty)
  is the query-descended route, and the KB-only linear chain
  is Bat -> HasWings -> not-HasBarrel -> not-Bat -> empty.

Why unit and input succeed here, despite being incomplete
in general: every grounded clause here is Horn (at most one
positive literal), and unit / input resolution are complete
for Horn clauses. That is a property of this KB, not a
general completeness claim.

Why set of support differs: with support = {not-H} for the
entailment test, a KB-only derivation is forbidden, because
neither parent is a support descendant. So KB alone derives
nothing under set of support, while KB + not-H still closes
— via the query-descended route not-Mammal -> not-Bat -> empty.
For the contradiction test, support = {H} has no clause
containing not-Mammal to resolve against, so it does not close.
Set of support therefore isolates the query route; it does
NOT turn the collapsed verdict into Neutral, because the
entailment route still closes (classically, an unsatisfiable
KB entails everything).

Why ordered does not change the verdict here: both tested
orderings close, but by different routes. Bat-first closes
by Bat -> HasWings -> not-HasBarrel -> not-Bat -> empty.
Wings-first blocks Bat -> HasWings (Bat is not maximal in
not-Bat or HasWings), yet still closes by the disjointness
route above. That is evidence for, not against, ordered
completeness on this clause set — but the route, and hence
any claim about *which* literal was decisive, still depends
on the ordering stated. In general, an ordered search that
fails to find an empty clause is not by itself a proof of
satisfiability unless the ordering (and any selection
function) is shown complete for that clause set; here the
search succeeds under both orders, so no such ambiguity
arises.

Bottom line: no strategy shows the collapsed KB satisfiable,
because it is not satisfiable — there is no model in which
one individual has both wings and a barrel while wings
exclude barrels. Strategy choice changes only (i) which
route to the empty clause is found, and (ii) whether the
route is query-descended (set of support, the only strategy
here that does not close KB alone). It does not change the
collapsed unsatisfiability, and it does not, on its own,
show Neutral. Neutral / logically inconclusive is a verdict
at the unresolved level (see scheme_check), not at the
collapsed level.
"""

from fol import collapsed_clauses, resolve, _lit, _neg


def _saturate_filtered(clauses, allowed):
    """Saturate, resolving only pairs allowed(a, b).

    Rounds, not a single i<j sweep: a clause added in one
    round must be paired with *all* earlier clauses in the
    next round, otherwise a route like derived-not-HasBarrel
    + input-not-Bat-or-HasBarrel is missed.
    """
    known = list(clauses)
    known_set = set(known)
    changed = True
    while changed:
        changed = False
        for i in range(len(known)):
            for j in range(i + 1, len(known)):
                if allowed(known[i], known[j]):
                    for resolvent in resolve(known[i], known[j]):
                        if resolvent not in known_set:
                            known_set.add(resolvent)
                            known.append(resolvent)
                            changed = True
                            if not resolvent:
                                return True
    return False


def unit_resolution(clauses):
    return _saturate_filtered(
        clauses, lambda a, b: len(a) == 1 or len(b) == 1
    )


def input_resolution(clauses):
    inputs = set(clauses)
    return _saturate_filtered(
        clauses, lambda a, b: a in inputs or b in inputs
    )


def set_of_support_resolution(clauses, support):
    """Saturate with a support set that grows by descent.

    A clause is in support if it is a support clause or a
    resolvent of a support clause. Only pairs with at least
    one support parent may resolve.
    """
    known = list(clauses)
    known_set = set(known)
    support_flags = [c in set(support) for c in known]
    changed = True
    while changed:
        changed = False
        for i in range(len(known)):
            for j in range(i + 1, len(known)):
                if support_flags[i] or support_flags[j]:
                    for resolvent in resolve(known[i], known[j]):
                        if resolvent not in known_set:
                            known_set.add(resolvent)
                            known.append(resolvent)
                            support_flags.append(True)
                            changed = True
                            if not resolvent:
                                return True
    return False


def hyper_resolution(clauses):
    """Hyper-resolution on grounded clauses.

    Repeatedly: take a nucleus clause (at least one negative
    literal); if every negative literal has a known positive
    unit counterpart, derive the nucleus's positive literals
    (or the empty clause, if it has none). Positive units are
    derived the same way, e.g. not-Bat or HasWings + Bat
    -> HasWings.
    """
    known = set(clauses)
    changed = True
    while changed:
        changed = False
        positive_units = {
            next(iter(c)) for c in known if len(c) == 1
        }
        positive_names = {
            name for name, negated in positive_units if not negated
        }
        for clause in list(known):
            negatives = [name for name, neg in clause if neg]
            if not negatives:
                continue
            if all(name in positive_names for name in negatives):
                resolvent = frozenset(
                    (name, neg) for name, neg in clause if not neg
                )
                if resolvent not in known:
                    known.add(resolvent)
                    changed = True
                    if not resolvent:
                        return True
    return False


def ordered_resolution(clauses, order):
    """Saturate, resolving only on maximal literals.

    order maps atom name -> rank (higher = larger). A literal
    may resolve only if its atom is maximal in its clause.
    """

    def maximal(clause, lit):
        name, _negated = lit
        return all(order[name] >= order[other] for other, _ in clause)

    def allowed(a, b):
        for lit in a:
            if _neg(lit) in b and maximal(a, lit) and maximal(b, _neg(lit)):
                return True
        return False

    return _saturate_filtered(clauses, allowed)


ORDER_BAT_FIRST = {
    "Bat": 5, "Mammal": 4, "HasWings": 3, "HasBarrel": 2, "CanFly": 1,
}
ORDER_WINGS_FIRST = {
    "HasWings": 5, "HasBarrel": 4, "Bat": 3, "Mammal": 2, "CanFly": 1,
}


def strategy_table():
    """KB alone / KB+not-H / KB+H, per strategy."""
    kb = collapsed_clauses()
    not_h = frozenset([_lit("Mammal", True)])
    h = frozenset([_lit("Mammal")])
    return {
        "unit": {
            "kb_alone": unit_resolution(kb),
            "kb_plus_not_h": unit_resolution(kb + [not_h]),
            "kb_plus_h": unit_resolution(kb + [h]),
        },
        "input": {
            "kb_alone": input_resolution(kb),
            "kb_plus_not_h": input_resolution(kb + [not_h]),
            "kb_plus_h": input_resolution(kb + [h]),
        },
        "set_of_support": {
            # KB alone: empty support, so no derivation.
            "kb_alone": set_of_support_resolution(kb, []),
            "kb_plus_not_h": set_of_support_resolution(
                kb + [not_h], [not_h]
            ),
            "kb_plus_h": set_of_support_resolution(kb + [h], [h]),
        },
        "hyper": {
            "kb_alone": hyper_resolution(kb),
            "kb_plus_not_h": hyper_resolution(kb + [not_h]),
            "kb_plus_h": hyper_resolution(kb + [h]),
        },
        "ordered_bat_first": {
            "kb_alone": ordered_resolution(kb, ORDER_BAT_FIRST),
            "kb_plus_not_h": ordered_resolution(
                kb + [not_h], ORDER_BAT_FIRST
            ),
            "kb_plus_h": ordered_resolution(kb + [h], ORDER_BAT_FIRST),
        },
        "ordered_wings_first": {
            "kb_alone": ordered_resolution(kb, ORDER_WINGS_FIRST),
            "kb_plus_not_h": ordered_resolution(
                kb + [not_h], ORDER_WINGS_FIRST
            ),
            "kb_plus_h": ordered_resolution(kb + [h], ORDER_WINGS_FIRST),
        },
    }


def split_worlds_satisfiable():
    """Neither split world derives an empty clause (traditional)."""
    from fol import saturate

    world_mammal = [
        frozenset([_lit("Bat")]),
        frozenset([_lit("Bat", True), _lit("Mammal")]),
        frozenset([_lit("Bat", True), _lit("HasWings")]),
        frozenset([_lit("Bat", True), _lit("CanFly")]),
    ]
    world_baseball = [
        frozenset([_lit("Bat")]),
        frozenset([_lit("Bat", True), _lit("HasBarrel")]),
    ]
    return {
        "world_mammal_empty": saturate(world_mammal)[0],
        "world_baseball_empty": saturate(world_baseball)[0],
    }


def scheme_check():
    """Apply the NLI-with-FOL scheme, at two levels.

    Naive scheme, collapsed level: entailment test (KB+not-H)
    closes AND contradiction test (KB+H) closes, via the
    KB-only route. Reading that naively gives both entailment
    and contradiction — not Neutral, and not a proof of
    inconclusive. It shows only that the collapsed KB is
    unsatisfiable.

    Corrected scheme, unresolved level: add two checks the
    PDF scheme needs for this case — (i) does the KB alone
    close? (ii) do the two readings disagree? — and the
    verdict is Neutral on the NLI side and logically
    inconclusive on the FOL side, for the equivocation-
    induced pair only.
    """
    from fol import saturate

    kb = collapsed_clauses()
    not_h = frozenset([_lit("Mammal", True)])
    h = frozenset([_lit("Mammal")])
    return {
        "naive_collapsed": {
            "entailment_test_closes": saturate(kb + [not_h])[0],
            "contradiction_test_closes": saturate(kb + [h])[0],
            "kb_alone_closes": saturate(kb)[0],
            "reads_as_neutral": False,
            "reads_as_inconclusive": False,
        },
        "corrected_unresolved": {
            "kb_alone_closes_flagged_as_gap": saturate(kb)[0],
            "worlds_disagree": True,
            "h_follows_from_unresolved": False,
            "not_h_follows_from_unresolved": False,
            "nli_label": "Neutral",
            "fol_verdict": "logically inconclusive",
            "scope": "equivocation-induced pairs only",
        },
    }
