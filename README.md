# Is NLI Neutral the same as logically inconclusive?

**For an equivocation-induced premise/hypothesis pair only — not for all Neutral pairs.**

Meta Global AI Developer Hackathon submission. Theoretical proof only.
No empirical evaluation. No evaluator.

## Question

Whether the Neutral label in Natural Language Inference (NLI) is the same
as saying logically inconclusive, when the obstruction is a homonymous
keyword — tested with a Meta Muse agent that proposes a memo and
independent verification checks, outside the model, that decide whether
it passes.

## Example

Premise (KB): "Bat is a mammal. Bat is used in baseball. Bats have wings.
Bats have a barrel. Wings are not barrels. Barrels are not wings. Bats can
fly. There is a Brown bat."

Hypothesis (query): "Brown bat is a mammal."

Abstract version, same structure with the keyword replaced by A:
"A is a mammal. A is used in baseball. A's have wings. A's have a barrel.
Wings are not barrels. Barrels are not wings. A's can fly. There is a
Brown A." Query: "Brown A is a mammal."

Whatever colour is used, the phrase is commonly grounded to one of the
two meanings of the homonymous keyword, by humans or by AI. First-order
logic does not require that grounding; it works with the predicates as given.

## Contributions

1. **Incoherent universals.** Forms such as "Xs have ABC" assert a property
   universally for two different meanings of X within the same premise,
   rendering an inconclusive inference and introducing equivocation.
2. **The collapsed model remains unsatisfiable, under every resolution
   procedure tested.** The KB-only empty clause does not go away by
   changing the resolution regime; what changes is whether it is misread
   as a query result.
3. **The NLI / FOL intersection.** For an equivocation-induced pair, when
   neither the entailment direction nor the contradiction direction is
   forced at the unresolved level, the pair is Neutral, due to logically
   inconclusive.

## How it works — Meta AI tooling, used beyond a basic integration

This is not a chat wrapper around a model, and the model is never trusted
on its own word.

- **Meta Model API only, at runtime.** Every model call goes to
  `https://api.meta.ai/v1`, fixed in `agent_kit/client.py`, to a Muse
  model (default `muse-wonder-1.0`, `muse-spark-1.3` if that is what
  the key covers). No other provider is called. The OpenAI SDK is used
  only as a client library, for persistent connections, timeouts, and
  retries — it needs no OpenAI key or subscription.
- **Muse as a resolution prover, not a chatbot.** For each of 7 resolution
  strategies (Traditional, Linear, Unit, Input, Set of Support, Hyper,
  Ordered) and each of 2 tests (KB AND NOT QUERY, KB AND QUERY), Muse is
  asked to do first-order resolution step by step on the grounded clauses
  and return JSON only: `empty_clause`, `derivation`, `route`
  (query-descended / kb-only / none). That is 28 Muse calls for
  Brown Bat + Brown A, every call and response logged to
  `logs/muse_calls.jsonl` with its NLI label (see Logging, below).
- **Muse proposing, proof disposing.** Each Muse result is cross-checked
  against a deterministic resolution engine. Agreement is recorded;
  disagreement is escalated, and the deterministic result is kept as
  the verdict. A wrong Muse derivation cannot silently become the table.
- **The legal-agent-workshop pattern, adapted.** Session 1: a general
  agent loop (`legal_agent/loop.py`) files a memo, choosing its own tools
  (list cases, read a case, check NLI, check FOL, submit memo, escalate).
  Session 2: verification checks sit inside the tools, outside the model.
  A verifier returns passed plus feedback; the agent sees only feedback;
  any score is reviewer-only. A finding that cannot be proven is escalated,
  not guessed — the demo stub first overclaims Entailment, is refused,
  then revises to Neutral / inconclusive, in 4 turns.

Two theory verifiers, plus memo rules: NLI theory (`nli.py`,
readings-based) and FOL theory (`fol.py`, grounded resolution).
The proof to verify against is the Results Table (`results_table.py`,
`RESULTS_TABLE.md`): columns NLI Label / Final Label, rows KB AND NOT
QUERY / KB AND QUERY, repeated for each resolution type, with one Muse
call per type per test recorded and cross-checked (`muse_prompts.md`,
`muse_results.json`, and the live log in Logging, below).

Two resolution procedures are used in the main design: traditional
(binary) resolution and linear resolution (most recent derived clause
as centre clause). Other strategies were also verified
(`resolution_strategies.py`): Unit, Input, Set of Support, Hyper,
Ordered (order: Bat > Mammal > HasWings > HasBarrel > CanFly).

## Results Table — collapsed KB, Brown Bat and Brown A (identical)

NLI Label is Neutral in every row (readings disagree).

| Resolution type | KB AND NOT QUERY: empty? | KB AND QUERY: empty? | Final Label |
|---|---|---|---|
| Traditional | Yes | Yes | cannot decide — both empty, collapsed KB unsatisfiable |
| Linear | Yes | Yes | cannot decide — both empty, collapsed KB unsatisfiable |
| Unit | Yes | Yes | cannot decide — both empty, collapsed KB unsatisfiable |
| Input | Yes | Yes | cannot decide — both empty, collapsed KB unsatisfiable |
| Set of Support | Yes | No | inconclusive inference (cannot decide) |
| Hyper | Yes | Yes | cannot decide — both empty, collapsed KB unsatisfiable |
| Ordered | Yes | Yes | cannot decide — both empty, collapsed KB unsatisfiable |

No collapsed row gives Neutral as a Final Label. That is the point:
collapsed resolution shows cannot decide, not Neutral.

Neutral as a Final Label appears only at the unresolved level: H is true
in the mammal world, false in the baseball world, neither follows —
Neutral in NLI, logically inconclusive in FOL.

Three terms are kept apart, deliberately: **Neutral** (NLI label, and
both-no-empty outcome), **inconclusive inference** (one empty, one
no-empty — cannot decide from the two tests alone), and **logically
inconclusive** (unresolved level, worlds disagree, neither follows).

## Model proof — Domain of discourse D

Following the proof sketch's Symbolic Logic method (`models.py`):
D is a non-empty set of abstract objects d1, d2, …; if c is a constant,
I(c) is in D; if P is a unary predicate, I(P) is a subset of D.

Example interpretation I0 (collapsed): D = {d1, d2}, I(Brown_Bat) = d1,
I(Bat) = {d1, d2}, I(HasWings) = {d1}, I(HasBarrel) = {d2}.
Wings are not barrels: {d1} ∩ {d2} = ∅, true. Bats have wings:
{d1, d2} ⊆ {d1}? No, false. Bats have a barrel: {d1, d2} ⊆ {d2}? No,
false. Barrels are not wings: ∅, true. I0 is not a model.

General proof: suppose I were a model, let d = I(Brown_Bat). Then
d ∈ I(Bat), so d ∈ I(HasWings) and d ∈ I(HasBarrel), contradicting
I(HasWings) ∩ I(HasBarrel) = ∅. Hence no interpretation satisfies the
collapsed KB: it is unsatisfiable, it has no mathematical model.
The same proof holds for Brown A, with A in place of Bat.

Reading models (unresolved): mammal model, H true; baseball model,
H false. Each is satisfiable on its own reading; they disagree on H.

## Run it — working demo, live

No key needed to see it work; a key is needed only to see a real
Muse call. Full setup, virtual environment, and troubleshooting
are in `SETUP.md`; the short version is here.

```bash
python3 -m unittest discover -s tests -v   # 21 tests, OK, no key needed
python3 run.py --results-table              # Results Table, Brown Bat + Brown A
python3 run.py --no-model --case brown_bat  # demo, answered in 4 turns
python3 run.py --no-model --case brown_a    # abstract case, same result
```

Expected demo result for both cases: `Status: answered`,
`Turns used: 4`, memo `nli_label: Neutral`,
`fol_claim: inconclusive`. The stub first overclaims
Entailment / entailed, is refused by the verifiers, then
revises to Neutral / inconclusive. That refuse / revise
loop is the check working.

For a real model run only: create a virtual environment,
install, set the key in that terminal (see `SETUP.md`):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export META_API_KEY='your-meta-key-here'
python3 run.py --case brown_bat
```

Do not install system-wide, and do not use `--break-system-packages`:
on Debian / Ubuntu based systems (including WSL), system Python is
externally managed and plain `pip install` fails with
`error: externally-managed-environment`. Use the venv above.
The code reads the key from the environment only — creating a
`.env` file alone does not set it; use `export META_API_KEY=...`
in that terminal, or `set -a; source .env; set +a` from a `.env`
file (never commit it, Unix line endings, no trailing `\r`).

## Entire pipeline, folder by folder

`run_pipeline.py` runs the whole pipeline in order, like the
legal-agent workshop (Session 1 loop, then Session 2 verification),
and stops at the first failing step — fix that step, do not
re-run everything from scratch:

```bash
python3 run_pipeline.py          # no key needed
python3 run_pipeline.py --real   # with a key: adds the Muse log, below
```

Order: (1) `tests/` — all tests; (2) Results Table; (3) `models.py`
— Domain D proof; (4) `resolution_strategies.py` — other strategies;
(5) end-to-end demo, `legal_agent/` loop + `agent_kit/` tools +
`verification/` verifiers + `cases/` — brown_bat, then brown_a;
(6) Muse verification log, only with `--real` and a key.

Each folder on its own:

```bash
# tests/ folder
python3 -m unittest discover -s tests -v

# Theory files at the root
python3 run.py --results-table
python3 -c "from models import evaluate_pdf_rules, pdf_interpretation; print(evaluate_pdf_rules(pdf_interpretation()))"

# cases/ folder
python3 -c "from cases import load_cases; print([c['id'] for c in load_cases('.')])"

# legal_agent/ + agent_kit/ + verification/ together — the Session 1 + 2 run
python3 run.py --no-model --case brown_bat
python3 run.py --no-model --case brown_a
python3 run.py --resume <run_id> --turns 15
```

`legal_agent/`, `agent_kit/`, and `verification/` have no separate
standalone commands, by design, as in the workshop: the loop calls
the tools, the tools call the verifiers, and `run.py` is the entry
point that runs them together.

## Logging — all Muse calls and responses, for both cases

`log_muse_calls.py` runs real Muse calls for the Results Table and
writes every call and response to a log file. It is also step 6 of
`run_pipeline.py --real`.

```bash
source .venv/bin/activate
export META_API_KEY='your-meta-key-here'
python3 log_muse_calls.py
```

Output: `logs/muse_calls.jsonl`, one JSON line per call, 28 lines
for a full run (2 cases × 7 strategies × 2 tests). Each line has:
timestamp, case_id, model, strategy, test, nli_label = Neutral
(every row, both cases), the exact prompt sent, the full Muse
response, empty_clause, route, deterministic empty_clause,
agree / escalated, and the NLI + FOL verifier result for the
Neutral / inconclusive memo for that case. No API key is ever
written to the log.

Loop Muse calls (the agent loop itself, not just resolution calls)
can be logged to the same file with `LoggingClient` from
`agent_kit/muse_log.py`, wrapped around `make_client()` before
passing it to `run_agent`; those appear as `kind=muse_loop`.

What is, and is not, a log — stated openly, so no record is
misread:

- `logs/muse_calls.jsonl` — the live Muse log. It exists only
  after a real run with a key. Without `--real` and a key, no
  Muse log is written at all: a stub log is not a Muse log,
  and this script refuses to write one.
- `workspace/<run_id>.json` — the loop log, created on every
  `run.py` run (demo and real), after every turn: run_id,
  status, turns used, timeline, messages, tool calls, tool
  results, final memo.
- `muse_results.json` — Muse results given in chat on
  2026-11-04, cross-checked against the deterministic table,
  agreeing on every row. A record, not a live API log; a live
  WSL run confirms or replaces it.
- `muse_prompts.md` — all 14 prompts (7 strategies × 2 tests),
  prompts only, no responses.
- `results_table_output.json` — deterministic table output,
  the proof, not a Muse log.

## Technical depth — and its limits, stated openly

- The engineering is a proof, not a demo script. Two honest
  corrections were found by running, not by reasoning alone:
  a saturation loop that missed new-vs-old clause pairs, and
  a wings-first ordered order that does close, contrary to a
  first guess. Set of Support is the sole exception in the
  table: Yes/No, where every other strategy is Yes/Yes.
- `fol.py` grounds universals to the queried individual, as in
  the proof sketch; it is not a full first-order prover.
  `nli.py` is readings-based, not a general NLI model.
- This tests equivocation-induced pairs with the Brown Bat /
  Brown A structure only. It does not prove the hypothesis
  for all Neutral pairs.
- Theoretical proof only. No empirical evaluation, no evaluator,
  by design. The 32-item prior dataset structure is referred
  to in `DATASET.md` as prior work only, not re-run or scored here.
- Lean formalisation is conditional only, if time permits, and
  is not started here.
- The collapsed KB's unsatisfiability is reported as a gap
  (`collapsed_model_unsatisfiable`), not hidden and not read
  as entailment.
- The sketch's C5 was written as NOT CanFly(Brown_Bat). CanFly is a
  premise, not the query, so it is not used as the negated query here;
  the negated query is NOT Mammal(Brown_Bat).

## Demo video (3 minutes)

1. The question, scoped to equivocation-induced pairs only (0:00–0:30).
2. Brown Bat in plain words + query (0:30–1:00).
3. Live no-key demo: Results Table, then brown_bat demo, answered
   in 4 turns, memo Neutral / inconclusive (1:00–2:00).
4. Verification layer: a refused overclaim, then the revised memo,
   then the Set of Support Yes/No row — the one row that is
   inconclusive inference, not Neutral (2:00–2:40).
5. Scope close: theoretical proof only, Meta models only,
   equivocation-induced pairs only (2:40–3:00).

## Files

`README.md` (this submission summary) · `SETUP.md` (full setup and
configuration, including venv and troubleshooting) · `THEORY.md` ·
`RESULTS_TABLE.md` · `FILE_GUIDE.md` (explains every file) ·
`VERIFICATION.md` · `DATASET.md` · `legal_agent/loop.py` ·
`agent_kit/` (client, progress, tools, muse_log) ·
`verification/` (NLI, FOL, memo rules) · `nli.py` · `fol.py` ·
`models.py` · `resolution_strategies.py` · `results_table.py` ·
`results_table_output.json` · `muse_resolution_calls.py` ·
`muse_prompts.md` · `muse_results.json` · `log_muse_calls.py` ·
`run_pipeline.py` · `run.py` · `cases/brown_bat.json` ·
`cases/brown_a.json` · `tests/` · `logs/muse_calls.jsonl`
(after a real run only) · `workspace/<run_id>.json` (runtime, git-ignored)
