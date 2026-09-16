"""Minimal standard-library request for an OpenAI-compatible Chat Completions endpoint."""

import json
import os
import urllib.error
import urllib.request

api_key = os.environ.get("OPENAI_API_KEY")
base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
model = os.environ.get("OPENAI_MODEL")

if not api_key:
    raise SystemExit("Set OPENAI_API_KEY first.")
if not model:
    raise SystemExit("Set OPENAI_MODEL to a model shown by your endpoint.")

payload = json.dumps({
    "model": model,
    "messages": [{"role": "user", "content": "Reply with one short sentence: what is a token?"}],
}).encode("utf-8")
request = urllib.request.Request(
    f"{base_url}/chat/completions",
    data=payload,
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    method="POST",
)

try:
    with urllib.request.urlopen(request, timeout=60) as response:
        body = json.load(response)
        print(json.dumps({
            "status": response.status,
            "model": body.get("model"),
            "usage": body.get("usage"),
            "finish_reason": (body.get("choices") or [{}])[0].get("finish_reason"),
            "text": ((body.get("choices") or [{}])[0].get("message") or {}).get("content"),
        }, ensure_ascii=False, indent=2))
except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8", errors="replace"))
    raise SystemExit(error.code)
