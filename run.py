"""Run one theory case through legal_agent.loop.

Real mode (needs a Meta Model API key, never printed):
    export MODEL_API_KEY=...
    python3 run.py --case brown_bat

Demo / test mode (no key, no model call; a deterministic stub
client that first overclaims, then revises on verifier
feedback — clearly labelled as a stub, not a model run):
    python3 run.py --no-model --case brown_bat

Resume a paused run:
    python3 run.py --resume <run_id> --turns 15

The reviewer score is never printed here: the loop returns
progress with memo, escalations, and timeline, and the
verifier scores live only in the verifier results, which
are stripped before they reach the model.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from legal_agent.loop import resume_run, run_agent  # noqa: E402


class _StubMessage:
    def __init__(self, tool_calls=None, content=""):
        self.content = content
        self.tool_calls = tool_calls or []


class _StubFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class _StubToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = _StubFunction(name, arguments)


class _StubChoice:
    def __init__(self, message):
        self.message = message


class _StubResponse:
    def __init__(self, message):
        self.choices = [_StubChoice(message)]


class _StubCompletions:
    """Deterministic stub: overclaim, then revise on refusal."""

    def __init__(self):
        self.calls = 0

    def create(self, model=None, messages=None, tools=None, tool_choice=None):
        self.calls += 1
        # Find the last tool result: if a memo was refused,
        # the next proposal is the corrected one.
        refused = any(
            isinstance(m, dict)
            and m.get("role") == "tool"
            and "not supported" in m.get("content", "")
            for m in (messages or [])
        )
        if not refused and self.calls == 1:
            # First turn: list, then read, then overclaim.
            # The stub does one tool per turn, in order.
            step = 1
        else:
            step = 99
        if self.calls == 1:
            call = _StubToolCall(
                "call_1", "list_cases", json.dumps({})
            )
        elif self.calls == 2:
            call = _StubToolCall(
                "call_2", "read_case", json.dumps({"case_id": "brown_bat"})
            )
        elif not refused:
            memo = {
                "nli_label": "Entailment",
                "nli_reason": "collapsed resolution",
                "fol_claim": "entailed",
                "fol_reason": "collapsed resolution",
            }
            call = _StubToolCall(
                "call_3",
                "submit_memo",
                json.dumps({"case_id": "brown_bat", "memo": memo}),
            )
        else:
            memo = {
                "nli_label": "Neutral",
                "nli_reason": "readings disagree: H true on mammal "
                "reading, false on baseball reading, lexeme unresolved",
                "fol_claim": "inconclusive",
                "fol_reason": "unresolved worlds disagree: H true in "
                "one satisfiable world, false in the other, "
                "neither follows from the unresolved pair",
            }
            call = _StubToolCall(
                "call_4",
                "submit_memo",
                json.dumps({"case_id": "brown_bat", "memo": memo}),
            )
        return _StubResponse(_StubMessage(tool_calls=[call]))


class _StubChat:
    def __init__(self):
        self.completions = _StubCompletions()


class StubClient:
    def __init__(self):
        self.chat = _StubChat()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default="brown_bat")
    parser.add_argument("--turns", type=int, default=30)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--no-model", action="store_true")
    parser.add_argument(
        "--results-table",
        action="store_true",
        help="Print the Results Table (Brown Bat + Brown A) and exit. "
        "This is the proof the verifiers check against.",
    )
    args = parser.parse_args()

    if args.results_table:
        from results_table import main_output

        print(json.dumps(main_output(), indent=1))
        return 0

    root = os.path.dirname(os.path.abspath(__file__))
    if args.no_model:
        print("Demo mode: stub client, no model call, no API key.")
        client = StubClient()
    else:
        from agent_kit.client import make_client

        client = make_client()

    if args.resume:
        result = resume_run(
            root=root, run_id=args.resume, client=client, turns=args.turns
        )
    else:
        result = run_agent(root=root, client=client, turns=args.turns)

    print("Run:", result["run_id"])
    print("Status:", result["status"])
    if result.get("reason"):
        print("Reason:", result["reason"])
    if result.get("memo"):
        print("Memo:", json.dumps(result["memo"], indent=2))
    if result.get("escalations"):
        print("Escalations:", json.dumps(result["escalations"], indent=2))
    print("Turns used:", result.get("turns_used"))
    print("Progress file: workspace/%s.json" % result["run_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
