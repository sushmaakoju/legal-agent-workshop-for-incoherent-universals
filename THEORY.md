# Theory note: incoherent universals, equivocation, Neutral

## Hypothesis

Whether Neutral in NLI is the same as logically inconclusive
**for an equivocation-induced premise/hypothesis pair.**

Not for all Neutral pairs. Only for pairs whose obstruction is a
homonymous keyword.

## Incoherent universals

Forms such as "Xs have ABC" that assert a property universally for
the two different meanings of X within the same premise, rendering
an inconclusive inference. Incoherent universals also introduce the
equivocation fallacy: a reasoner that treats the head as one
predicate can move from one meaning to the other without noticing.

Brown Bat is the concrete instance:

- Meaning 1 (mammal animal): bat is a mammal, bats have wings,
  bats can fly.
- Meaning 2 (baseball equipment): bat is used in baseball, bats
  have a barrel.
- Disjointness, as property exclusion in this scaffold: wings are
  not barrels, barrels are not wings.

## Two renderings — do not collapse them

### 1. Collapsed, single-predicate rendering

One predicate `Bat`, grounded to the queried individual
`Brown_Bat` (see the simplification note below):

- `Bat(Brown_Bat)`
- `Bat(x) -> Mammal(x)`, `Bat(x) -> HasWings(x)`,
  `Bat(x) -> HasBarrel(x)`, `Bat(x) -> CanFly(x)`
- `HasWings(x) -> not HasBarrel(x)`

Resolution on the KB alone derives an empty clause via the
wings / barrel route, without ever using the negated query.
So the collapsed KB has **no mathematical model**: no
interpretation can give one individual both wings and a barrel
while wings exclude barrels.

Consequence, and the core caution: an empty clause from the
collapsed KB alone does **not** show that the query was entailed
or contradicted. Under traditional resolution both the
entailment test (KB + not-H) and the contradiction test
(KB + H) close via that same KB-only route. That is a property
of the incoherent KB, not evidence about H.

The verifiers therefore refuse any memo that claims "entailed
by collapsed resolution" or "contradicted by collapsed
resolution" on that basis alone.

### 2. Unresolved, two-worlds rendering

Keep the string "Brown bat is a mammal" unresolved, and read it
in two satisfiable worlds:

- World 1 (mammal reading): the individual is a mammal bat.
  H is true there.
- World 2 (baseball reading): the individual is baseball
  equipment. H is false there (baseball bats are not mammals).

Neither H nor not-H follows from the unresolved pair, because
the worlds disagree and the lexeme has not been disambiguated.
That joint failure — neither direction forced — is what this
project calls **logically inconclusive**, and it is the
configuration annotated **Neutral** on the NLI side.

That is the anchor for the NLI / FOL intersection:
equivocation-induced, not split-predicate. If you split the
meanings into `Bat1` / `Bat2` up front and then treat them as
independent, you have erased the equivocation you were trying
to study. The split is used here only to *exhibit* the two
worlds, not to replace the unresolved pair.

## Two resolution procedures used — and only these two

Per the author's key input on 2026-11-04, this project uses
**two** FOL resolution procedures, not the full list in that
input (unit, input, set-of-support, hyper, ordered resolution
are background strategies, not used here):

1. **Traditional resolution** — binary resolution, resolving
   exactly two clauses at a time (combined with factoring in
   full FOL; factoring is vacuous on the grounded clauses
   here), run to saturation. Sound and refutation-complete
   for FOL.
2. **Linear resolution** — the most recently derived clause
   (the centre clause) is one parent at every step; the other
   parent is an input clause or an ancestor of the centre
   clause. Complete with factoring in full FOL.

Both close the collapsed KB on its own, without the negated
query — traditional by saturation, linear by the centre chain
Bat → HasWings → not-HasBarrel → not-Bat → empty clause
(see `fol.py: linear_resolve`). Set-of-support, discussed in
the earlier sketch, is **not** one of the two procedures used
in this version.

## Other strategies checked — same collapsed verdict

Verified in `resolution_strategies.py` (grounded KB, 13 tests
passing in this VM), using the same approach as the proof
sketch: KB alone, KB + not-H, KB + H.

- Unit, input, hyper, and ordered (two orderings tested):
  empty clause in all three cases. Unit and input succeed
  here because every grounded clause is Horn (at most one
  positive literal), for which they are complete — not a
  general completeness claim.
- Set of support: the only exception. KB alone: no empty
  clause (empty support, no KB-only derivation allowed).
  KB + not-H: empty, via the query-descended route
  not-Mammal -> not-Bat -> empty. KB + H: no empty clause.
  So set of support isolates the query route, but does not
  make the collapsed verdict Neutral — the entailment route
  still closes, as it must for an unsatisfiable KB, which
  classically entails everything.
- Split worlds: neither world derives an empty clause under
  any strategy tested — each world is satisfiable on its own
  reading.

No other strategy shows the collapsed KB satisfiable, because
it is not satisfiable. Strategy choice changes the route,
and (for set of support) whether the route is query-descended.
It does not change the collapsed verdict.

## Does the NLI-with-FOL scheme give Neutral / inconclusive?

Yes — but only with two checks added, and only at the
unresolved level. The scheme in `NLI-with-FOL.pdf` is:

- NLI side: premise true, must H be true? (entailment),
  must H be false? (contradiction), neither? (Neutral).
- FOL side: KB + not-H -> empty? (entailment),
  KB + H -> empty? (contradiction), neither? (inconclusive).

Applied naively to the collapsed KB, that scheme does **not**
give Neutral: both tests close, via the KB-only route, so it
reads as both entailment and contradiction. That is a
diagnosis of unsatisfiability, not of Neutral.

Applied with (i) a KB-alone check — if the KB alone closes,
flag it as a collapsed-model gap and do not read test
closures as query evidence — and (ii) a worlds-disagreement
check — H true in the mammal world, false in the baseball
world — the scheme gives, for the equivocation-induced pair
only: NLI Neutral, FOL logically inconclusive. That corrected
scheme is what `resolution_strategies.scheme_check()` encodes,
and what the two verifiers enforce: a memo claiming entailment
or contradiction from collapsed resolution alone is refused.

## Contributions claimed for this scaffold

1. Incoherent universals, as defined above.
2. Despite both resolution procedures used here — traditional
   and linear — the collapsed model remains unsatisfiable:
   the KB-only empty clause does not go away by changing the
   resolution regime; what changes is whether the empty clause
   is (mis)read as a query result.
3. The NLI / FOL intersection: for an equivocation-induced
   pair, when neither the entailment direction nor the
   contradiction direction is forced at the unresolved level,
   the pair is taken as Neutral, due to logically inconclusive.

## Simplification, stated openly

This scaffold grounds the universals to the queried individual
(`Brown_Bat` / `Brown_A`) instead of implementing full
first-order unification. That is enough to exhibit the
wings / barrel empty clause and the two-worlds disagreement,
and it is the same simplification the proof sketch uses with
clauses C1–C5. It is **not** a full FOL prover.

Open points carried over from the sketch, not hidden:

- "There is a Brown bat" is treated here as the constant
  `Brown_Bat`. The existential reading
  (exists x: Brown(x) and Bat(x)) is a separate formalisation
  choice and is not decided by this scaffold.
- The disjointness clause is read as property exclusion
  (nothing has both wings and a barrel), not as a strict
  object-identity claim.
- Lean formalisation, if time permits, would have to fix both
  choices explicitly before it could count as a proof.
