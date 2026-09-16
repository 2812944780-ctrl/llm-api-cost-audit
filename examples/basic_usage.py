"""Minimal example: log usage from any OpenAI-compatible endpoint.

Setup
-----
    pip install -r requirements.txt
    export OPENAI_API_KEY=sk-...            # Windows: set OPENAI_API_KEY=sk-...
    export OPENAI_BASE_URL=https://api.openai.com/v1
    export OPENAI_MODEL=gpt-4o-mini

Run
---
    python examples/basic_usage.py
    python -m audit report usage.jsonl
"""

import os

from openai import OpenAI

from audit import UsageLogger

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY", "YOUR_KEY"),
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
)

logger = UsageLogger("usage.jsonl", tag="demo")

response = client.chat.completions.create(
    model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    messages=[
        {"role": "system", "content": "Answer in one short sentence."},
        {"role": "user", "content": "Explain what a token is."},
    ],
)

row = logger.log(response, task_id="demo-0001")
print(row)
print()
print("Now run:  python -m audit report usage.jsonl")
