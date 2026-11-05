# Verification contract

This file is the contract for the two theory verifiers, in the
same spirit as the workshop's `VERIFICATION.md`.

- Each verifier is a function `run_verification(memo)` in
  `verification/`.
- It returns `passed` plus `feedback`. The agent sees only
  that feedback.
- A `score`, if present, goes to the reviewer / console only,
  never to the agent. `agent_loop.py` strips it before
  feedback, and `run.py` hides it unless `--show-reviewer`
  is passed.
- Verifiers sit inside the tools, not as agent-chosen tools.
  The agent does not choose which verifier runs, or when.
- A finding that cannot be proven from its cited clause or
  reading is escalated, not marked proven. Escalation is a
  legitimate terminal state for that finding, not a failure
  to be papered over by guessing.
- No verifier quotes, paraphrases, or counts ground-truth
  items: there is no ground truth in this project, only the
  Brown Bat / Brown A cases and the clause / readings checks
  in `fol.py` and `nli.py`.
