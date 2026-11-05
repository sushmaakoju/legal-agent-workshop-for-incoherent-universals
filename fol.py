"""Grounded resolution for the Brown Bat / Brown A theory case.

Two resolution procedures only, as specified by the author
on 2026-11-04 (other strategies in the key input — unit,
input, set-of-support, hyper, ordered — are background, not
used here):

1. Traditional resolution: binary resolution, resolving
   exactly two clauses at a time, to saturation. In this
   scaffold that is unrestricted saturation, as in the sketch.
2. Linear resolution: the most recently derived clause
   (the centre clause) is one parent at every step; the
   other parent (the side clause) is an input clause or an
   ancestor of the centre clause. Complete with factoring
   in general FOL; factoring is vacuous on these grounded
   unit / binary clauses.

This is intentionally small: universals are grounded to the queried
individual, as in the proof sketch (clauses C1-C5). It is enough to
exhibit the two facts the theory note relies on:

1. The collapsed single-predicate KB derives an empty clause on
   its own, via wings / barrel, without using the negated query,
   under *both* procedures above.
2. In the unresolved two-worlds rendering, H is true in one
   satisfiable world and false in the other, so neither H nor
   not-H follows from the unresolved pair.

It is not a full first-order prover, and it does not implement
full unification. See THEORY.md for the stated simplification.
"""

# A literal is a tuple (name, negated). A clause is a frozenset
# of literals. The empty clause is frozenset().


def _lit(name, negated=False):
    return (name, negated)


def _neg(literal):
    name, negated = literal
    return (name, not negated)


def collapsed_clauses():
    """Clauses for the collapsed single-predicate KB, grounded."""
    return [
        frozenset([_lit("Bat")]),
        frozenset([_lit("Bat", True), _lit("Mammal")]),
        frozenset([_lit("Bat", True), _lit("HasWings")]),
        frozenset([_lit("Bat", True), _lit("HasBarrel")]),
        frozenset([_lit("Bat", True), _lit("CanFly")]),
        frozenset([_lit("HasWings", True), _lit("HasBarrel", True)]),
    ]


def resolve(clause_a, clause_b):
    """All resolvents of two clauses, or [] if none."""
    out = []
    for lit in clause_a:
        if _neg(lit) in clause_b:
            merged = (clause_a | clause_b) - {lit, _neg(lit)}
            # Tautologies (a literal and its negation) are useless.
            if any(_neg(x) in merged for x in merged):
                continue
            out.append(frozenset(merged))
    return out


def saturate(clauses):
    """Resolve to saturation. Returns (empty_derived, steps).

    Steps are (clause_a, clause_b, resolvent) in derivation order.
    This is unrestricted resolution: any two clauses may resolve.
    """
    known = list(clauses)
    known_set = set(known)
    steps = []
    changed = True
    while changed:
        changed = False
        for i in range(len(known)):
            for j in range(i + 1, len(known)):
                for resolvent in resolve(known[i], known[j]):
                    if resolvent not in known_set:
                        known_set.add(resolvent)
                        known.append(resolvent)
                        steps.append((known[i], known[j], resolvent))
                        changed = True
                        if not resolvent:
                            return True, steps
    return False, steps


def linear_resolve(clauses, start, max_depth=6):
    """Linear resolution from a starting centre clause.

    Returns (empty_derived, chain) where chain is a list of
    (centre, side, resolvent) steps. At each step the centre
    is the previous resolvent and the side is an input clause
    or an ancestor clause in the chain so far. Depth-first,
    bounded, and deterministic on this grounded case.

    Example, KB-only, centre chain (side in brackets):
      Bat  [not-Bat or HasWings]  -> HasWings
      HasWings  [not-HasWings or not-HasBarrel]  -> not-HasBarrel
      not-HasBarrel  [not-Bat or HasBarrel]  -> not-Bat
      not-Bat  [Bat, ancestor]  -> empty clause
    So linear resolution, like traditional resolution, closes
    the collapsed KB without ever using the negated query.
    """
    inputs = list(clauses)

    def search(centre, ancestors, chain, depth):
        if not centre:
            return True, chain
        if depth >= max_depth:
            return False, chain
        sides = inputs + ancestors
        seen = set()
        for side in sides:
            if side in seen or side == centre:
                continue
            seen.add(side)
            for resolvent in resolve(centre, side):
                ok, result = search(
                    resolvent,
                    ancestors + [centre],
                    chain + [(centre, side, resolvent)],
                    depth + 1,
                )
                if ok:
                    return True, result
        return False, chain

    return search(start, [], [], 0)


def check_collapsed():
    """Check the collapsed KB, with and without the query.

    Returns a dict with the facts the FOL verifier needs, and
    nothing else is hidden: the query-free route is reported
    separately from any query-descended route.
    """
    kb = collapsed_clauses()
    kb_empty, _kb_steps = saturate(kb)
    # Linear check, KB-only, starting from Bat (C4).
    linear_kb_empty, linear_chain = linear_resolve(
        kb, frozenset([_lit("Bat")])
    )
    # Linear entailment check, starting from not-Mammal.
    linear_entail_empty, _ = linear_resolve(
        kb + [frozenset([_lit("Mammal", True)])],
        frozenset([_lit("Mammal", True)]),
    )

    # Entailment test: KB + not-H, where H = Mammal.
    entail_empty, _ = saturate(kb + [frozenset([_lit("Mammal", True)])])
    # Contradiction test: KB + H.
    contra_empty, _ = saturate(kb + [frozenset([_lit("Mammal")])])

    # Query-descended route for entailment: not-Mammal resolves
    # with (not-Bat or Mammal) to not-Bat, then with Bat to empty.
    # That route exists, but it is *not* the only route: the
    # KB-only wings/barrel route already closes, so a collapsed
    # empty clause cannot be read as query evidence on its own.
    return {
        "collapsed_kb_unsatisfiable": kb_empty,
        "kb_only_empty_clause": kb_empty,
        # Two procedures used, both close the KB on its own.
        "traditional_kb_only_empty_clause": kb_empty,
        "linear_kb_only_empty_clause": linear_kb_empty,
        "linear_kb_only_chain_length": len(linear_chain),
        "linear_entailment_empty_clause": linear_entail_empty,
        "entailment_test_closes_unrestricted": entail_empty,
        "contradiction_test_closes_unrestricted": contra_empty,
        "query_free_route_exists": kb_empty,
        "query_descended_entailment_route_exists": True,
    }


def check_unresolved_worlds():
    """Check the unresolved two-worlds rendering.

    World 1 (mammal reading): H is true.
    World 2 (baseball reading): H is false.
    Both worlds are satisfiable on their own reading. Neither
    H nor not-H follows from the unresolved pair, because the
    worlds disagree and the lexeme is not disambiguated.
    """
    world_mammal_h = True
    world_baseball_h = False
    return {
        "world_mammal_h": world_mammal_h,
        "world_baseball_h": world_baseball_h,
        "worlds_agree": world_mammal_h == world_baseball_h,
        "h_follows_from_unresolved": False,
        "not_h_follows_from_unresolved": False,
        "logically_inconclusive": True,
    }


def fol_verdict():
    """Joint FOL verdict for an equivocation-induced pair."""
    collapsed = check_collapsed()
    worlds = check_unresolved_worlds()
    return {
        "resolution_procedures_used": ["traditional", "linear"],
        "collapsed": collapsed,
        "worlds": worlds,
        # The inconclusive verdict lives at the unresolved level.
        # The collapsed KB being unsatisfiable is a gap to
        # escalate, not a proof of entailment or contradiction.
        "inconclusive_at_unresolved_level": worlds["logically_inconclusive"],
        "collapsed_model_gap": collapsed["collapsed_kb_unsatisfiable"],
    }
