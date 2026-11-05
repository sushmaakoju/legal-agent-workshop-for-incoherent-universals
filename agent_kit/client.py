"""Create an SDK client for the Meta Model API only.

Kept deliberately as the OpenAI SDK, not raw requests: the
SDK (via httpx) reuses persistent connections, and handles
timeouts and retries on transient delays, instead of opening
a fresh connection per call.

This is NOT an OpenAI account and does NOT need an OpenAI
key or subscription. "OpenAI" here is only the SDK library.
Every call goes to the Meta Model API, and only to a Muse
model, because:

- base_url is fixed to https://api.meta.ai/v1 (it is not
  left at the SDK default, and it is not overridable to
  another provider in this project);
- api_key is your Meta key, read from META_API_KEY (with
  MODEL_API_KEY as a fallback for the workshop setup), and
  is never printed or logged;
- model defaults to muse-wonder-1.0, the Muse model in the
  author's example. If your key only has muse-spark-1.3
  access, set MODEL_NAME=muse-spark-1.3 instead.

The client itself is created here, in run.py / by the caller,
and passed into legal_agent.loop.run_agent. The loop never
creates a client and never reads an API key.
"""

from __future__ import annotations

import os

from openai import OpenAI

META_BASE_URL = "https://api.meta.ai/v1"


def make_client() -> OpenAI:
    key = (
        os.environ.get("META_API_KEY", "").strip()
        or os.environ.get("MODEL_API_KEY", "").strip()
    )
    if not key:
        raise RuntimeError(
            "No Meta API key is set. Set META_API_KEY (or "
            "MODEL_API_KEY) in the environment or in a .env "
            "file that is never committed; do not paste it "
            "in chat. No OpenAI key is needed."
        )
    return OpenAI(
        api_key=key,
        base_url=META_BASE_URL,
        timeout=120,
        max_retries=2,
    )


def model_name() -> str:
    return os.environ.get("MODEL_NAME", "muse-wonder-1.0")
