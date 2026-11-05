"""Run the entire pipeline, folder by folder, like the legal-agent workshop.

Order, mirroring Session 1 -> Session 2 in the workshop:
  1. tests/            — all unit tests (theory, loop, strategies,
                         results table, models)
  2. results_table.py  — Results Table, Brown Bat + Brown A
                         (the proof the verifiers check against)
  3. models.py         — Domain D model proof check
  4. resolution_strategies.py — other strategies check
  5. legal_agent/ + agent_kit/ + verification/ + cases/
                       — end-to-end demo runs, no model, no key:
                         brown_bat, then brown_a. The loop proposes,
                         the tools run the verifiers, a memo is
                         refused then revised, then filed.
  6. Real model run    — ONLY if --real is passed AND a Meta key
                         is set in this terminal (META_API_KEY or
                         MODEL_API_KEY). Otherwise skipped, clearly
                         labelled, not an error.

Usage (no key needed for steps 1-5):
  python3 run_pipeline.py
  python3 run_pipeline.py --real   # real Muse run, needs key + venv SDK

Exit code 0 only if every step that ran passed. A skipped real
run does not fail the pipeline.
"""

import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def run_step(name, cmd, env=None):
    print(f"\n=== {name} ===", flush=True)
    print(f"$ {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=ROOT, env=env)
    ok = result.returncode == 0
    print(f"--- {name}: {'PASS' if ok else 'FAIL'} ---", flush=True)
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--real", action="store_true")
    args = parser.parse_args()

    steps = []
    # 1. tests/ — every folder's tests, in one suite.
    steps.append(run_step(
        "1. tests/ (all folders)",
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
    ))
    # 2. Results Table.
    steps.append(run_step(
        "2. results_table.py (proof to verify against)",
        [sys.executable, "run.py", "--results-table"],
    ))
    # 3. Domain D models.
    steps.append(run_step(
        "3. models.py (Domain D proof)",
        [sys.executable, "-c",
         "from models import evaluate_pdf_rules, pdf_interpretation, "
         "prove_no_collapsed_model; "
         "print(evaluate_pdf_rules(pdf_interpretation())); "
         "print(prove_no_collapsed_model()['conclusion'])"],
    ))
    # 4. Other strategies.
    steps.append(run_step(
        "4. resolution_strategies.py (other strategies)",
        [sys.executable, "-c",
         "from resolution_strategies import strategy_table; "
         "import json; print(json.dumps(strategy_table(), indent=1))"],
    ))
    # 5. End-to-end pipeline, like legal-agent Session 1 + 2:
    #    loop (legal_agent/) + tools (agent_kit/) + verifiers
    #    (verification/) + cases (cases/), demo mode, no key.
    steps.append(run_step(
        "5a. End-to-end demo: brown_bat (legal_agent + agent_kit + verification)",
        [sys.executable, "run.py", "--no-model", "--case", "brown_bat"],
    ))
    steps.append(run_step(
        "5b. End-to-end demo: brown_a (abstract case)",
        [sys.executable, "run.py", "--no-model", "--case", "brown_a"],
    ))
    # 6. Muse verification log, only if asked and keyed:
    #    all Muse calls + responses, both cases, all
    #    strategies, both tests, NLI labels, to
    #    logs/muse_calls.jsonl (see log_muse_calls.py).
    if args.real:
        steps.append(run_step(
            "6. Muse verification log (brown_bat + brown_a, all strategies)",
            [sys.executable, "log_muse_calls.py"],
        ))
    else:
        print("\n=== 6. Muse verification log: SKIPPED (no --real flag; "
              "a stub log is not a Muse log, so none is written) ===",
              flush=True)
    # 7. Real model run, only if asked and keyed.
    if args.real:
        key = os.environ.get("META_API_KEY") or os.environ.get("MODEL_API_KEY")
        if not key:
            print("\n=== 6. Real model run: SKIPPED (no META_API_KEY / "
                  "MODEL_API_KEY in this terminal) ===", flush=True)
        else:
            steps.append(run_step(
                "6. Real model run: brown_bat (Meta Muse only)",
                [sys.executable, "run.py", "--case", "brown_bat"],
            ))
    else:
        print("\n=== 6. Real model run: SKIPPED (no --real flag; "
              "no key needed for steps 1-5) ===", flush=True)

    if all(steps):
        print("\nPIPELINE: ALL STEPS PASSED", flush=True)
        return 0
    print("\nPIPELINE: FAILED — see the FAIL step above; "
          "do not re-run the whole pipeline, fix that step first.",
          flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
