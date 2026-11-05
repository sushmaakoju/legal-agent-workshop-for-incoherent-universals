"""Log every Meta Muse call and response, never the API key.

Log format: one JSON object per line, in logs/muse_calls.jsonl
under the project root, unless another path is given.
Each record has, at least:
  timestamp, case_id, kind, model, strategy, test,
  nli_label, prompt (or messages summary), response,
  empty_clause, route, deterministic_empty_clause, agree,
  verifier_passed, verifier_feedback, source.

kind is one of:
  "muse_resolution" — one Muse call per strategy per test,
    per case, from muse_resolution_calls.py.
  "muse_loop" — one Muse call from the agent loop
    (legal_agent/loop.py), wrapped by LoggingClient.
  "verification" — one verifier check on a memo, with the
    memo's NLI label, recorded alongside the Muse call it
    verifies.

No record ever contains an API key, a .env value, or a
full message history with credentials. Prompts and tool
arguments are recorded because they are the proof being
verified; the key is never part of a prompt.

In demo / stub mode, source is "stub", not "muse", and the
log is labelled as such. A stub log is not a Muse log.
A real Muse log requires --real and META_API_KEY (or
MODEL_API_KEY) in the terminal, with the venv SDK installed.
"""

import json
import os
from datetime import datetime, timezone


def log_path_for(root, name="muse_calls.jsonl"):
    path = os.path.join(str(root), "logs", name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def write_log(path, record):
    record = dict(record)
    record.setdefault(
        "timestamp",
        datetime.now(timezone.utc).isoformat(),
    )
    # Never log a key, even if a caller passes one by mistake.
    record.pop("api_key", None)
    record.pop("META_API_KEY", None)
    record.pop("MODEL_API_KEY", None)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    return record


class _LoggingCompletions:
    def __init__(self, inner, log_path, context):
        self._inner = inner
        self._log_path = log_path
        self._context = context or {}

    def create(self, **kwargs):
        response = self._inner.create(**kwargs)
        try:
            message = response.choices[0].message
            content = getattr(message, "content", "") or ""
            tool_calls = []
            for call in getattr(message, "tool_calls", None) or []:
                fn = getattr(call, "function", None)
                tool_calls.append({
                    "id": getattr(call, "id", ""),
                    "name": getattr(fn, "name", "") if fn else "",
                    "arguments": getattr(fn, "arguments", "") if fn else "",
                })
        except Exception:
            content, tool_calls = "", []
        write_log(self._log_path, {
            **self._context,
            "kind": "muse_loop",
            "model": kwargs.get("model", ""),
            "request_messages": kwargs.get("messages", []),
            "response_content": content,
            "response_tool_calls": tool_calls,
            "source": "muse",
        })
        return response


class _LoggingChat:
    def __init__(self, inner_chat, log_path, context):
        self.completions = _LoggingCompletions(
            inner_chat.completions, log_path, context
        )


class LoggingClient:
    """Wrap a real Muse client so every loop call is logged.

    Usage: client = LoggingClient(make_client(), log_path, context)
    then pass client to legal_agent.loop.run_agent. The loop
    calls client.chat.completions.create exactly as before;
    this wrapper only adds a log line per call.
    """

    def __init__(self, inner, log_path, context=None):
        self._inner = inner
        self.chat = _LoggingChat(inner.chat, log_path, context or {})
