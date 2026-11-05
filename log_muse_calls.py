"""Log all Meta Muse calls and responses, for both cases,
all resolution types, both tests, with NLI labels.

Output: logs/muse_calls.jsonl under the project root,
one JSON line per Muse call (28 lines for a full run:
2 cases x 7 strategies x 2 tests), plus verification
records for the Neutral / inconclusive memo for each case.
Each line has: timestamp, case_id, kind, model, strategy,
test, nli_label (Neutral, every row), prompt, response,
empty_clause, route, deterministic_empty_clause, agree,
escalated, source, verification (NLI + FOL passed/feedback).

Usage (real Muse only, needs key + venv SDK):
  source .venv/bin/activate
  export META_API_KEY='your-meta-key-here'
  python3 log_muse_calls.py
  python3 log_muse_calls.py --log logs/muse_calls.jsonl

This script does NOT run in demo/stub mode: a stub log is
not a Muse log. If no key is set, it stops with a clear
error instead of writing fake Muse rows. The deterministic
table is the cross-check, not a substitute for a Muse call.

To also log loop Muse calls (the agent loop, not just
resolution calls), use LoggingClient from agent_kit/muse_log
around make_client() before passing it to run_agent; those
calls are logged as kind=muse_loop to the same file.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_kit.muse_log import log_path_for


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default=None)
    args = parser.parse_args()

    key = os.environ.get("META_API_KEY") or os.environ.get("MODEL_API_KEY")
    if not key:
        print("No META_API_KEY (or MODEL_API_KEY) set in this terminal. "
              "Export it first, then retry. No log was written.")
        return 1

    from agent_kit.client import make_client
    from muse_resolution_calls import record_muse_results

    root = os.path.dirname(os.path.abspath(__file__))
    log_path = args.log or log_path_for(root)
    total = 0
    for case_id in ("brown_bat", "brown_a"):
        rows = record_muse_results(
            make_client(), case_id=case_id, log_path=log_path
        )
        total += len(rows)
        print(f"{case_id}: {len(rows)} Muse calls logged, "
              f"agree={sum(1 for r in rows if r['agree'])}/"
              f"{len(rows)}, escalated="
              f"{sum(1 for r in rows if r['escalated'])}")
    print(f"Log: {log_path} ({total} Muse calls, NLI label Neutral throughout)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
