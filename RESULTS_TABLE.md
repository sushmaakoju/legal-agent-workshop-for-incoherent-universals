# Results Table — Brown Bat and abstract Brown A

## Prerequisite (author's steps, verbatim structure)

Columns: **NLI Label, Final Label**
Rows, per resolution type:
- Row 1: KB AND NOT QUERY (entailment test, QUERY = "Brown bat / Brown A is a mammal", so NOT QUERY = NOT Mammal)
- Row 2: KB AND QUERY (contradiction test)

Empty clause = contradiction in the refutation sense (the test closes).
No empty clause = the test does not close.

## Step 1 — one row alone cannot decide

- KB AND NOT QUERY, empty → entailment candidate.
  No empty → neutral or contradiction (row alone cannot decide).
- KB AND QUERY, empty → contradiction candidate.
  No empty → neutral or entailed; this row-level undecided state is called
  "inconclusive" in step 1. It is not step 4's "inconclusive inference",
  and not "logically inconclusive" at the unresolved level (see Terms below).

## Steps 2 and 4 — both rows together

- Both rows no empty clause → **Neutral** (step 2).
- One row empty, the other no empty clause → **cannot decide, called
  "inconclusive inference"** (step 4).
- Both rows empty → **cannot decide** for a separate reason, labelled
  separately here rather than forced into step 4's mixed wording:
  the collapsed KB itself is unsatisfiable, so both tests close vacuously
  via the KB-only route and neither is query evidence.

## Terms — do not collapse these three

- **Neutral**: NLI label (readings disagree), and step 2's both-no-empty outcome.
- **Inconclusive inference**: step 4's mixed outcome, cannot decide from
  the two resolution tests alone.
- **Logically inconclusive**: unresolved-level FOL verdict — H true in one
  satisfiable world, false in the other, neither H nor NOT H follows.
  This is a positive verdict about the unresolved pair, not a failure to decide.

## Step 3 — Muse calls

For each type and each test, call Muse, record its result, then cross-check
against the deterministic engine (see `muse_resolution_calls.py`). Agreement
is recorded; disagreement is escalated and the deterministic result is kept
as the verdict. A Muse call proposes, it does not prove — otherwise Session 2
would trust the model it is meant to check.

In this VM no API key is available, so no live Muse call was run here.
The table below is the deterministic engine's result, which is what a Muse
call in WSL (with META_API_KEY, Muse model only) would be cross-checked
against. Do not relabel a deterministic row as a Muse row until that call
has actually been run and recorded.

## Step 5 — filled results, collapsed KB

NLI Label is Neutral in every row (readings disagree: H true on the mammal
reading, false on the baseball reading). Final Label is the combined label
from steps 2/4 above. Ordered resolution order, as requested:
**Bat > Mammal > HasWings > HasBarrel > CanFly**
(Brown A: A > Mammal > HasWings > HasBarrel > CanFly).

### Brown Bat — collapsed KB

| Resolution type | KB AND NOT QUERY: empty? | KB AND QUERY: empty? | NLI Label | Final Label |
|---|---|---|---|---|
| Traditional | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Linear | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Unit | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Input | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Set of Support | Yes | No | Neutral | inconclusive inference (cannot decide) |
| Hyper | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Ordered (order above) | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |

### Brown A (abstract) — collapsed KB, Bat renamed to A

Identical to Brown Bat, by renaming, run in `results_table.py` (not copy-pasted).
The abstract case is the invariance check: replacing the homonymous keyword
with A does not change any empty / no-empty result, any NLI label, or any
Final Label.

| Resolution type | KB AND NOT QUERY: empty? | KB AND QUERY: empty? | NLI Label | Final Label |
|---|---|---|---|---|
| Traditional | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Linear | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Unit | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Input | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Set of Support | Yes | No | Neutral | inconclusive inference (cannot decide) |
| Hyper | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |
| Ordered (order above, A first) | Yes | Yes | Neutral | cannot decide — both empty, collapsed KB unsatisfiable (vacuous) |

Note what is *not* in either collapsed table: no row gives Neutral as a
Final Label. That is the point. Collapsed resolution does not show Neutral;
it shows cannot decide (both empty, or, for Set of Support, inconclusive
inference). Neutral as a Final Label appears only at the unresolved level:

### Unresolved pair (both cases) — where Neutral / logically inconclusive sit

| Test | Forces? | NLI Label | Final Label / FOL verdict |
|---|---|---|---|
| KB AND NOT QUERY (does NOT H follow?) | No | Neutral | Neutral / logically inconclusive |
| KB AND QUERY (does H follow?) | No | Neutral | Neutral / logically inconclusive |

H true in the mammal world, false in the baseball world, neither follows.
Scope: equivocation-induced pairs only, not all Neutral pairs.

## Step 7 — Symbolic Logic proof, Domain of discourse D

Following proof-sketch-summary.pdf, section "By Symbolic Logic proof method:
Domain of discourse D" (full proof in `models.py`):

- D is a non-empty set of abstract objects d1, d2, ...
- If c is a constant, I(c) is in D. If P is a unary predicate, I(P) is a
  subset of D. I is the mapping function assigning constants and predicates.
- Sketch example interpretation I0 (collapsed): D = {d1, d2},
  I(Brown_Bat) = d1, I(Bat) = {d1, d2}, I(HasWings) = {d1}, I(HasBarrel) = {d2}.
  - Rule 1, wings are not barrels: {d1} ∩ {d2} = ∅ → TRUE.
  - Rule 2, bats have wings: {d1, d2} ⊆ {d1}? No (d2 has no wings) → FALSE.
  - Rule 3, bats have a barrel: {d1, d2} ⊆ {d2}? No (d1 has no barrel) → FALSE.
  - Rule 4, barrels are not wings: {d2} ∩ {d1} = ∅ → TRUE.
  I0 is not a model of the KB; it falsifies rules 2 and 3.
- General proof (not just I0): suppose I were a model, let d = I(Brown_Bat).
  Bat(Brown_Bat) gives d ∈ I(Bat); bats have wings gives d ∈ I(HasWings);
  bats have a barrel gives d ∈ I(HasBarrel); wings are not barrels gives
  I(HasWings) ∩ I(HasBarrel) = ∅ — contradiction. Hence no interpretation
  satisfies the collapsed KB: it is unsatisfiable, it has no mathematical model.
- Reading models (unresolved): mammal model D = {d1}, H true; baseball model
  D = {d1}, H false. Each is satisfiable on its own reading; they disagree on H.
- Abstract Brown A: same proof with A in place of Bat, I(Brown_A) = d1,
  I(A) = {d1, d2}, I(HasWings) = {d1}, I(HasBarrel) = {d2}, same evaluations,
  same contradiction. The proof is isomorphic, not a second, different proof.

Correction preserved from the confirmed query: the sketch's C5 was written as
NOT CanFly(Brown_Bat). CanFly is a premise, not the query, so it is not used
as the negated query here. The negated query is NOT Mammal(Brown_Bat).

## How to regenerate this table

```bash
python3 -m unittest discover -s tests -v
python3 -c "from results_table import build_table; import json; print(json.dumps(build_table('brown_bat'), indent=1)); print(json.dumps(build_table('brown_a'), indent=1))"
```
