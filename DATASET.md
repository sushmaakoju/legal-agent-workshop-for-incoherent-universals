# Dataset reference

Source, referred to by the author for this project:
https://sushmaakoju.github.io/human-ai-collaborated-ai4science/

## What that site documents (prior work, not this project's result)

- A toy knowledge-base dataset for logical inconclusiveness,
  organised as a structured wiki plus an agentic simulation.
- The dataset viewer is described as 32 items: **8 polysemous KB
  keys × 4 query types**, with per-item logic and NLI verdicts.
- The simulation file is named on the site as
  `logically-inconclusive-kbs/kbs/combined.jsonl`.
- The prior three-agent simulation on that site is Logic Expert,
  NLI Expert, and Reasoning Coordinator. Its reported MCQ
  accuracy (71.9%) is a prior-work result, **not** a result of
  this hackathon project, and it must not be presented as one.

## How this project uses that reference

This hackathon project is theoretical proof only, with no
empirical evaluation and no evaluator. So it does **not**
re-run the 32-item evaluation, does not score accuracy, and
does not reproduce the 32 items as its own dataset.

It uses the dataset only as a *pattern*:

- A case is a premise / hypothesis pair built around one
  homonymous keyword, with two meanings, incoherent universals
  (properties of both meanings asserted universally), property
  disjointness, and one queried individual.
- The query types in the schema are the four kinds a case can
  take: an inconclusive / Neutral query, a conclusive query,
  a meaning-specific query, and a colour-variant query. Only
  the first kind is the equivocation-induced hypothesis tested
  here; the others are schema placeholders, not evaluated
  claims in this project.

## Cases actually included here

- `cases/brown_bat.json` — the hand-curated Brown Bat case,
  fully specified, with premise and query as confirmed by the
  author.
- `cases/brown_a.json` — the abstract Brown A case, same
  structure, keyword replaced by the placeholder `A`.
- `cases/dataset_schema.json` — the field schema for an
  8 × 4 case set, so a future case set can be added without
  changing the loop or the verifiers.

## If you have the original combined.jsonl

If you hold a copy of `combined.jsonl` that you are entitled
to use, drop it in `cases/dataset/combined.jsonl`. The loader
in `cases.py` will read it (one JSON object per line, with at
least `id`, `premise`, and `hypothesis`) and add those cases
to `list_cases`. It does not score them, and it does not
change the theoretical scope. Do not commit an API key, a
`.env` file, or a private dataset file to a public repo.
