"""The Legal Agent: the agentic loop.

run_agent works the case; resume_run continues a run that stopped.

One turn is: ask the model what to do next, run the one tool
it picks (if any) with tools.run_tool, send the result back,
and save progress. The loop stops when a tool result says the
run is over (memo filed and passed, or a finding escalated),
or at the turn limit. On the last turn, the model is told to
file a memo or escalate, not to start new work.

The model chooses every tool call. The code does not hard-code
which tool runs when, and it does not contain case-specific
logic: the case data lives in cases/, the theory checks live
in verification/, and the tools in agent_kit/tools are fixed.
A verifier result returned to the model contains passed +
feedback only; scores are reviewer-facing and are kept out
of tool results (see agent_kit/tools and VERIFICATION.md).
"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:  # Tests use a stub client; real runs need openai.
    OpenAI = object  # type: ignore

from agent_kit.progress import load_progress, save_progress
from agent_kit.tools import TOOL_DEFINITIONS, run_tool
from cases import load_cases

SYSTEM_PROMPT = (
    "You are a theory agent working one equivocation-induced "
    "premise/hypothesis case at a time. Use the tools: list "
    "cases, read a case, check an NLI or FOL claim, file a "
    "memo with submit_memo, or escalate a finding you cannot "
    "prove. Do not guess a finding to get past a refusal. "
    "If a verifier refuses a memo, revise it to match what "
    "its quotes, clauses, or readings actually support, or "
    "escalate that finding. A memo must state its NLI label "
    "and its FOL claim, with a reason for each."
)

INITIAL_PROMPT = (
    "Work one theory case. Start by listing cases, then read "
    "one case, check your claims, and file a memo for it "
    "with submit_memo. Do not file a memo for a case you "
    "have not read."
)


def _get(obj, name, default=None):
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _tool_calls(message):
    calls = _get(message, "tool_calls") or []
    out = []
    for call in calls:
        function = _get(call, "function") or {}
        args_raw = _get(function, "arguments") or "{}"
        try:
            args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
        except json.JSONDecodeError:
            args = {}
        out.append(
            {
                "id": _get(call, "id") or str(uuid.uuid4()),
                "name": _get(function, "name") or "",
                "arguments": args,
            }
        )
    return out


def _message_dict(message):
    content = _get(message, "content")
    tool_calls = _tool_calls(message)
    result = {"role": "assistant", "content": content or ""}
    if tool_calls:
        result["tool_calls"] = [
            {
                "id": c["id"],
                "type": "function",
                "function": {
                    "name": c["name"],
                    "arguments": json.dumps(c["arguments"]),
                },
            }
            for c in tool_calls
        ]
    return result


def _call_model(client, messages):
    # Meta Muse only: the client itself is fixed to
    # https://api.meta.ai/v1 in agent_kit/client.py, and the
    # model defaults to muse-wonder-1.0 (see that file).
    model = os.environ.get("MODEL_NAME", "muse-wonder-1.0")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
    )
    choices = _get(response, "choices") or []
    if not choices:
        raise RuntimeError("model returned no choices")
    return _get(choices[0], "message")


def _run_loop(root: Path, client: OpenAI, progress: dict, turns: int) -> dict:
    messages = progress.setdefault("messages", [])
    if not messages:
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "user", "content": INITIAL_PROMPT})

    for _ in range(turns):
        progress["turns_used"] = progress.get("turns_used", 0) + 1
        is_last = progress["turns_used"] >= progress.get(
            "turn_budget", progress["turns_used"]
        )
        # The turn budget is set by run_agent / resume_run before
        # this loop runs; on the final turn, tell the model to
        # close, not to start new work.
        if is_last:
            messages.append(
                {
                    "role": "user",
                    "content": "This is your last turn: file a memo "
                    "with submit_memo, or escalate the finding "
                    "you cannot prove. Do not start new work.",
                }
            )
        try:
            message = _call_model(client, messages)
        except Exception as exc:  # Save state, then report, not hide.
            progress["status"] = "error"
            progress["error"] = str(exc)
            save_progress(root, progress)
            return progress

        messages.append(_message_dict(message))
        calls = _tool_calls(message)
        step = {
            "turn": progress["turns_used"],
            "content": _get(message, "content"),
            "tool_calls": [c["name"] for c in calls],
        }
        progress.setdefault("timeline", []).append(step)

        if not calls:
            save_progress(root, progress)
            continue

        for call in calls:
            try:
                result = run_tool(root, call["name"], call["arguments"], progress)
            except Exception as exc:
                result = {"passed": False, "feedback": str(exc)}
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": json.dumps(result),
                }
            )
            step.setdefault("tool_results", []).append(
                {"tool": call["name"], "result": result}
            )
            if result.get("status") == "answered":
                progress["status"] = "answered"
                save_progress(root, progress)
                return progress
            if result.get("status") == "escalated":
                progress["status"] = "escalated"
                save_progress(root, progress)
                return progress
        save_progress(root, progress)

    progress["status"] = "paused"
    progress["reason"] = "Hit the turn limit"
    save_progress(root, progress)
    return progress


def run_agent(*, root: Path, client: OpenAI, turns: int = 30) -> dict:
    root = Path(root)
    run_id = uuid.uuid4().hex[:12]
    cases = load_cases(root)
    progress = {
        "run_id": run_id,
        "status": "running",
        "turns_used": 0,
        "turn_budget": turns,
        "case_ids": [c["id"] for c in cases],
        "memo": None,
        "case_id": None,
        "escalations": [],
        "escalated_gaps": [],
        "timeline": [],
        "messages": [],
    }
    save_progress(root, progress)
    # turn_budget is the total budget for this run, so the
    # last-turn prompt fires on the final turn of this call.
    return _run_loop(root, client, progress, turns)


def resume_run(*, root: Path, run_id: str, client: OpenAI, turns: int = 15) -> dict:
    root = Path(root)
    progress = load_progress(root, run_id)
    if progress.get("status") == "answered":
        return progress
    # Continue from the saved messages and timeline, with a
    # fresh budget of `turns` additional turns.
    progress["status"] = "running"
    progress["turn_budget"] = progress.get("turns_used", 0) + turns
    progress.pop("reason", None)
    progress.pop("error", None)
    save_progress(root, progress)
    return _run_loop(root, client, progress, turns)
