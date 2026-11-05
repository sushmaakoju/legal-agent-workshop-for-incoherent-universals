# File guide — every file in this folder, what it means, why we have it

## How to run it (short, from README.md)

```bash
pip install -r requirements.txt   # OpenAI SDK, only for real model runs
python3 -m unittest discover -s tests -v
python3 run.py --no-model --case brown_bat    # demo, no key, stub client, labelled
python3 run.py --no-model --case brown_a      # abstract case, same demo
# Real mode, Meta Model API only, Muse model only:
export META_API_KEY=...   # or MODEL_API_KEY as fallback; never paste it in chat
python3 run.py --case brown_bat
python3 run.py --resume <run_id> --turns 15
```

Theory checks and tests need no key and no model call. That is deliberate:
the checks must not trust the model. Real model runs have not been tested
in WSL on the author's laptop; do not present this as WSL-tested until
run there.

## Docs — the argument, in words

- `README.md` — scope, folder structure, loop contract, how to run, and
  honest limits. Why: the packet's entry point; judges and the author
  should not have to read code to know what is claimed and what is not.
- `THEORY.md` — hypothesis (Neutral = logically inconclusive, only for
  equivocation-induced pairs), incoherent universals, collapsed vs
  unresolved renderings, two procedures used, other strategies checked,
  and the corrected NLI-with-FOL scheme. Why: the theory the code
  implements; without it the code is just clauses.
- `RESULTS_TABLE.md` — the prerequisite Results Table: columns NLI Label /
  Final Label, rows KB AND NOT QUERY / KB AND QUERY, steps 1–7, filled
  results for Brown Bat and Brown A, and the Domain D model proof summary.
  Why: the table the author asked for, in one place, with terms kept apart.
- `VERIFICATION.md` — Session 2 contract: `run_verification` returns passed
  + feedback, agent sees only feedback, score is reviewer-only, unprovable
  findings are escalated not guessed. Why: the rule the verifiers follow,
  so a passing memo is not just a model saying "trust me".
- `DATASET.md` — the 8 × 4 / 32-item structure at
  sushmaakoju.github.io/human-ai-collaborated-ai4science/, labelled prior
  work only, not re-run or scored here. Why: to refer to that background
  without turning it into an empirical evaluation, which is out of scope.
- `FILE_GUIDE.md` — this file. Why: so each file's purpose is stated
  once, in the project itself, not only in chat.

## Entry point — running one case

- `run.py` — CLI. Real mode (Meta key, Muse model) and `--no-model` demo
  mode (deterministic stub client that first overclaims Entailment /
  entailed, is refused by the verifiers, then revises to Neutral /
  inconclusive — clearly labelled as a stub, not a model run), plus
  `--resume <run_id>`. Why: one command to run a case, without needing
  the legal workshop's console.
- `requirements.txt` — `openai>=1.0` only. Why: the SDK is a client library
  for the Meta API; it needs no OpenAI key or subscription. See client.py.
- `.env.example` — template for META_API_KEY / MODEL_API_KEY and MODEL_NAME
  (default muse-wonder-1.0, muse-spark-1.3 if that is what the key covers).
  Why: to show the key names without ever committing a real key.
- `.gitignore` — ignores `.env`, `__pycache__`, and `workspace/` run files.
  Why: keys and runtime state must not be committed.

## The loop — Session 1 pattern, general, not case-specific

- `legal_agent/__init__.py` — package marker, no logic. Why: Python needs
  it to import `legal_agent.loop`.
- `legal_agent/loop.py` — `run_agent(*, root, client, turns=30)` and
  `resume_run(*, root, run_id, client, turns=15)`, with the exact stub
  signatures requested. One turn: ask the model what to do next, run the
  one tool it picks, send the result back, save progress. Stops on memo
  filed + passed, on escalation, or at the turn limit; on the last turn
  it tells the model to file or escalate, not start new work. Why: this
  is the general agent; it contains no Brown Bat, NLI, or FOL logic —
  that belongs in the verification layer, not the loop.
- `agent_kit/__init__.py` — package marker.
- `agent_kit/client.py` — `make_client()` and `model_name()`. Base URL is
  fixed to https://api.meta.ai/v1, key is META_API_KEY (MODEL_API_KEY
  fallback), model defaults to muse-wonder-1.0, timeout 120, retries 2.
  The SDK reuses persistent connections and handles delays, which is why
  it was kept instead of raw `requests`. Why: every model call in the
  project goes through here, so Meta-only routing is enforced in one place.
- `agent_kit/progress.py` — save / load `workspace/<run_id>.json`.
  Why: a run can pause (turn limit, waiting for a person) and resume
  without losing its messages, memo, or escalations.
- `agent_kit/tools/__init__.py` — the tools the model may call:
  `list_cases`, `read_case`, `check_nli`, `check_fol`, `submit_memo`,
  `escalate`. Tools sit inside the loop, not as model-chosen verifiers:
  the model chooses which tool and when, but the tools and verifiers are
  fixed code. Tool results give the model passed + feedback only; scores
  and escalated gaps are kept in progress, reviewer-facing only.
  Why: this is the Session 2 boundary — the model proposes, fixed code decides.

## Theory engines — deterministic, no model call

- `nli.py` — `nli_label()`: readings-based NLI label. Mammal reading H
  true, baseball reading H false, readings disagree, neither forced →
  Neutral. Why: the NLI side of the bridge, computed from readings, not
  from a model call, so `verify_nli_theory` has something independent
  to check against.
- `fol.py` — grounded resolution for the theory case: `collapsed_clauses()`,
  `resolve()`, `saturate()` (traditional), `linear_resolve()` (centre
  chain), `check_collapsed()`, `check_unresolved_worlds()`, `fol_verdict()`.
  Why: the FOL side of the bridge. It shows the collapsed KB closes on
  its own under both used procedures, and the unresolved worlds disagree,
  so neither H nor NOT H follows at the unresolved level.
- `models.py` — Symbolic Logic proof method with Domain of discourse D,
  following proof-sketch-summary.pdf: D, interpretation function I
  (constants → D, unary predicates → subsets of D), the sketch's example
  interpretation I0 (D = {d1, d2}, I(Brown_Bat) = d1, I(Bat) = {d1, d2},
  I(HasWings) = {d1}, I(HasBarrel) = {d2}), rule-by-rule evaluation
  (rules 1 and 4 true, 2 and 3 false under I0), the general proof that no
  collapsed model exists (d in both HasWings and HasBarrel contradicts
  their empty intersection), and the two reading models (mammal H true,
  baseball H false). Why: resolution alone shows an empty clause; models
  show *why* there is no model, in the sketch's own explanation style.
  The sketch's C5 (NOT CanFly) is not used as the query here, because
  CanFly is a premise; the negated query is NOT Mammal.
- `resolution_strategies.py` — verification appendix for the other
  strategies: Unit, Input, Set of Support, Hyper, Ordered (two orders
  tested), plus split-world checks and `scheme_check()`. Why: to answer,
  with code, whether any other strategy changes the collapsed verdict.
  It does not, except Set of Support, which does not close KB alone.
  This file does not change the two procedures used in the main design.
- `results_table.py` — the Results Table as code: per strategy, per case,
  KB AND NOT QUERY / KB AND QUERY empty or not, row labels (step 1),
  combined labels (steps 2/4, plus both-empty labelled separately),
  NLI Label, and the unresolved table. Why: so the table in
  RESULTS_TABLE.md is generated and tested, not hand-typed and stale.
  Run it with `python3 results_table.py` or `python3 run.py --results-table`.
- `results_table_output.json` — the generated output of `results_table.py`
  for Brown Bat, Brown A, and the unresolved table. Why: so the table
  exists as a file to open, not only as code that computes it.
- `muse_results.json` — Muse results per strategy per test, recorded in
  chat (Muse, 2026-11-04, step 3), cross-checked against the deterministic
  engine, agree on every row. Why: step 3's recording step, in a file.
  A live API call via `muse_resolution_calls.py` in WSL would confirm /
  replace these rows; it has not been run in this VM (no key).
- `muse_resolution_calls.py` — step 3 interface: prompt template and
  `ask_muse_resolution()` / `record_muse_results()` for one Muse call
  per strategy per test, with deterministic cross-check; disagreement
  is escalated, deterministic result kept. Why: to record Muse results
  in the table without letting a Muse call become the proof. No live
  call was run in this VM (no key); do not relabel a deterministic row
  as a Muse row until a call has actually been run in WSL and recorded.
- `muse_prompts.md` — all 14 filled-in prompts (7 strategies × 2 tests),
  generated from that template, so the prompts can be read without
  importing the SDK. Why: so the exact Muse prompts are visible as a
  file, not hidden inside code that needs `pip install -r requirements.txt`.

## Verification — Session 2, outside the model

- `verification/__init__.py` — package marker.
- `verification/verify_nli_theory.py` — `run_verification(memo, case)`:
  memo's NLI label must match the expected label (or `nli.py`'s label)
  and its reason must be supported by readings disagreement. Why: the
  NLI theory check, independent of the model.
- `verification/verify_fol_theory.py` — `run_verification(memo, case)`:
  memo's FOL claim must match `fol_verdict()` AND the Results Table
  (`results_table.build_table()`): collapsed combined labels are all
  cannot decide (both empty) except Set of Support, inconclusive
  inference, so entailed / contradicted from collapsed resolution
  alone is refused against the table itself. Why: verify means check
  against this proof, not just against a separate verdict function.
  This wiring was added in the audit fix on 2026-11-04, after it was
  found missing.
- `verification/verify_memo.py` — structural memo rules: memo must have
  an NLI label and a FOL claim, and must not overclaim from a signed /
  only / sequence statement unless escalated. Why: the memo-rules layer
  from the workshop, so a well-labelled memo with an unsupported reason
  still fails.

## Cases — concrete and abstract, both considered

- `cases.py` — `load_cases()` / `get_case()`, including optional
  `cases/dataset/combined.jsonl` if supplied (not included). Why: the
  loop and tools load cases through one loader, not by hard-coding paths.
- `cases/brown_bat.json` — the concrete, hand-curated case: colour Brown,
  keyword Bat, meanings mammal animal / baseball equipment, properties
  wings / barrel, premise (the confirmed KB), hypothesis "Brown bat is a
  mammal.", expected NLI Neutral, expected FOL inconclusive,
  query_type inconclusive_neutral. Why: this is the author's confirmed
  example; everything else is built around it.
- `cases/brown_a.json` — the abstract case, same structure with the
  homonymous keyword replaced by placeholder A: premise "A is a mammal.
  A is used in baseball. A's have wings. A's have a barrel. Wings are not
  barrels. Barrels are not wings. A's can fly. There is a Brown A.",
  hypothesis "Brown A is a mammal.", same expected labels. Why: the
  invariance check — if the argument depends on the word "bat" rather
  than on equivocation itself, it fails here. It does not: the Results
  Table and the Domain D proof for Brown A are identical to Brown Bat
  under renaming Bat → A (see `results_table.abstract_clauses()` and
  `models.abstract_pdf_interpretation()`), and `run.py --case brown_a`
  runs it end to end. The abstract case is considered in every table,
  every model, and every test, not mentioned once and dropped.
- `cases/dataset_schema.json` — 8 × 4 schema for the prior 32-item
  dataset (8 polysemous keys × 4 query types). Why: to state the schema
  of the prior work referred to in DATASET.md, without including or
  re-scoring that dataset here.

## Tests — what is actually checked, in this VM

- `tests/test_theory.py` — collapsed KB unsatisfiable, unresolved worlds
  inconclusive, NLI Neutral, two procedures only (traditional + linear),
  verifiers refuse entailment overclaim, verifiers pass corrected memo,
  memo rules refuse signed overclaim. Why: the theory claims, tested.
- `tests/test_loop.py` — loop answers with stub, paused run resumes to
  answered, unknown run_id raises. Why: the loop contract, tested.
- `tests/test_strategies.py` — strategy table (unit/input/hyper/ordered
  close everywhere, Set of Support KB-alone no / entailment yes /
  contradiction no), split worlds satisfiable, scheme (naive collapsed
  both close, not Neutral; corrected unresolved Neutral / inconclusive).
  Why: the other-strategies claims, tested, including the two corrections
  found by running (saturation pairing, ordered route).
- `tests/test_results_table.py` — Results Table values for Brown Bat,
  Brown A identical by renaming, combined-label rules, unresolved
  Neutral / logically inconclusive. Why: the table in RESULTS_TABLE.md,
  tested, not hand-typed.
- `tests/test_models.py` — PDF interpretation rules (1/4 true, 2/3 false),
  abstract rules identical, reading models disagree on H, no-collapsed-
  model proof present. Why: the Domain D proof, tested.

## Runtime state — not source

- `workspace/.gitkeep` — placeholder so the `workspace/` directory exists
  in the zip. Why: progress files (`workspace/<run_id>.json`) are written
  here at run time and are git-ignored; the zip contains no run files,
  no `__pycache__`, no `.env`.
