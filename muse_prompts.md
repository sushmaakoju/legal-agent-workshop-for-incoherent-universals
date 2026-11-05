# Prompts to Muse for verifying each FOL resolution

One prompt per strategy per test. 7 strategies x 2 tests = 14 prompts.

Clauses (grounded, Brown Bat; for Brown A replace Bat with A):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test 1 = KB AND NOT QUERY (add NOT Mammal). Test 2 = KB AND QUERY (add Mammal).
Ordered order: Bat > Mammal > HasWings > HasBarrel > CanFly (A first for Brown A).
These prompts are also in muse_resolution_calls.py as PROMPT_TEMPLATE, used by ask_muse_resolution().

## Traditional — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Traditional

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Traditional — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Traditional

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Linear — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Linear

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Linear — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Linear

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Unit — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Unit

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Unit — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Unit

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Input — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Input

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Input — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Input

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Set of Support — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Set of Support

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Set of Support — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Set of Support

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Hyper — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Hyper

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Hyper — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Hyper

Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Ordered — kb_and_not_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Ordered
Ordered resolution order: Bat > Mammal > HasWings > HasBarrel > CanFly (A > Mammal > HasWings > HasBarrel > CanFly for Brown A); resolve only on maximal literals.
Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND NOT QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".


## Ordered — kb_and_query

You are doing first-order resolution, step by step, for one test.

Resolution strategy: Ordered
Ordered resolution order: Bat > Mammal > HasWings > HasBarrel > CanFly (A > Mammal > HasWings > HasBarrel > CanFly for Brown A); resolve only on maximal literals.
Clauses (grounded, Brown Bat / Brown A case):
Bat (unit); NOT Bat OR Mammal; NOT Bat OR HasWings; NOT Bat OR HasBarrel; NOT Bat OR CanFly; NOT HasWings OR NOT HasBarrel. For Brown A, replace Bat with A throughout.

Test: KB AND QUERY
- If the test is KB AND NOT QUERY, add the clause NOT Mammal.
- If the test is KB AND QUERY, add the clause Mammal.

Follow ONLY the named strategy. Do not use another strategy
to fill a gap. Derive resolvents one step at a time, using
unification on these grounded clauses (factoring is vacuous
here). Stop when you derive the empty clause, or when no
further resolvent is possible under this strategy.

Return JSON only, exactly:
{"empty_clause": true_or_false,
  "derivation": ["step 1", "step 2"],
  "route": "query-descended" or "kb-only" or "none"}

"route" is "query-descended" only if a step uses the added
query clause or a clause derived from it; otherwise, if the
empty clause is derived, "route" is "kb-only".

