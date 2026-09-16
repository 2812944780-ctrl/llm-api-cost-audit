"""Generate a sample usage log so you can try the report without any API key.

    python examples/make_sample_log.py
    python -m audit report sample-usage.jsonl

The generated log deliberately contains a retry storm, prompt-token variance
and context-heavy calls, so every detector has something to find.
"""

import json
import random
from datetime import datetime, timedelta, timezone

random.seed(7)
start = datetime.now(timezone.utc) - timedelta(hours=6)
rows = []


def add(offset, tag, prompt, completion, task_id=None, finish="stop"):
    rows.append(
        {
            "ts": (start + offset).isoformat(timespec="seconds"),
            "tag": tag,
            "task_id": task_id,
            "model": "demo-model",
            "request_id": f"req-{len(rows):04d}",
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": prompt + completion,
            "finish_reason": finish,
        }
    )


# Normal summarise traffic with a slightly unstable prefix.
for i in range(40):
    add(
        timedelta(minutes=i * 5),
        "summarise",
        random.randint(1100, 1450),
        random.randint(250, 420),
        task_id=f"doc-{i:04d}",
    )

# Smaller translate calls, different shape entirely.
for i in range(25):
    add(
        timedelta(minutes=i * 4),
        "translate",
        random.randint(180, 260),
        random.randint(90, 160),
        task_id=f"tr-{i:04d}",
    )

# A retry storm: the same task id twice within seconds.
add(timedelta(minutes=133), "summarise", 1284, 396, task_id="doc-0042")
add(timedelta(minutes=133, seconds=4), "summarise", 1284, 402, task_id="doc-0042")
add(timedelta(minutes=180), "summarise", 1310, 380, task_id="doc-0107")
add(timedelta(minutes=180, seconds=2), "summarise", 1310, 391, task_id="doc-0107")
add(timedelta(minutes=180, seconds=5), "summarise", 1310, 377, task_id="doc-0107")

# Context-heavy calls: the input dominates the bill.
for i in range(6):
    add(
        timedelta(minutes=300 + i * 3),
        "rag-answer",
        random.randint(9000, 12000),
        random.randint(200, 400),
        task_id=f"rag-{i:02d}",
    )

with open("sample-usage.jsonl", "w", encoding="utf-8") as fh:
    for row in rows:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"Wrote {len(rows)} rows to sample-usage.jsonl")
print("Now run:  python -m audit report sample-usage.jsonl")
