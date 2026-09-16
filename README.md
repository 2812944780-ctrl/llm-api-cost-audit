# LLM API Cost Audit

Log real `usage` data from any **OpenAI-compatible** endpoint, then surface the three most common sources of hidden cost.

> Most "my bill doesn't match my estimate" problems are **not** overcharging. They come from **how you estimate**. This toolkit replaces guessing with recorded facts.

[中文说明 →](README.zh-CN.md) · [Deep Space API setup](docs/using-deep-space-api.md) · [Claude Code](docs/claude-code.md) · [Codex CLI](docs/codex-cli.md) · [CC Switch](docs/cc-switch.md) · [Errors](docs/errors.md) · [Streaming](docs/streaming.md)

> This repository does not provide free credits or trial quotas. Use an endpoint you already trust, or choose a paid plan after checking its current price, limits, and billing rules.

---

## Why estimates always fail

The naive formula is:

```
estimated_cost = input_chars * input_price + output_chars * output_price
```

It is structurally wrong, for four reasons:

| # | Reason | What actually happens |
|---|---|---|
| 1 | **Token ≠ characters** | Chinese, code, punctuation and emoji tokenize at very different ratios. Character-based reverse-engineering drifts. |
| 2 | **Input is bigger than you think** | `system` prompt, conversation history, RAG chunks and tool/function schemas are all billed. They routinely dwarf the user message. |
| 3 | **Caching changes the unit price** | Repeated prefixes may be billed at a lower rate — *when* they hit is not something you can assume. |
| 4 | **Retries double-bill** | On timeout the server may have already generated (and billed) tokens. Your retry pays again. |

This tool targets #3 and #4 directly, because they are invisible without a log.

---

## Install

```bash
git clone https://github.com/2812944780-ctrl/llm-api-cost-audit.git
cd llm-api-cost-audit
pip install -r requirements.txt
```

No third-party dependencies beyond the `openai` SDK.

## Examples and guides

- Python SDK: `examples/basic_usage.py`
- Python standard library: `examples/python/chat_completion.py`
- Node.js 18+: `examples/nodejs/chat-completion.mjs`
- curl on Linux/macOS: `examples/curl/chat-completion.sh`
- PowerShell on Windows: `examples/curl/chat-completion.ps1`
- [Deep Space API setup](docs/using-deep-space-api.md)
- [Claude Code configuration checks](docs/claude-code.md)
- [Codex CLI configuration checks](docs/codex-cli.md)
- [CC Switch configuration checks](docs/cc-switch.md)
- [HTTP error troubleshooting](docs/errors.md)
- [Streaming troubleshooting](docs/streaming.md)

All examples read credentials from environment variables. They do not write keys to files.

---

## Quick start

Wrap any call with `UsageLogger`:

```python
import os
from openai import OpenAI
from audit import UsageLogger

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://your-endpoint/v1",   # any OpenAI-compatible endpoint
)
logger = UsageLogger("usage.jsonl")

resp = client.chat.completions.create(
    model="your-model-name",
    messages=[
        {"role": "system", "content": "You are a careful technical assistant."},
        {"role": "user", "content": "Summarise the attached document."},
    ],
)

row = logger.log(resp, tag="summarise", task_id="doc-0001")
print(row)
```

```
{'ts': '2026-09-16T10:22:41+00:00', 'tag': 'summarise', 'task_id': 'doc-0001',
 'model': '...', 'prompt_tokens': 1284, 'completion_tokens': 396,
 'total_tokens': 1680, 'finish_reason': 'stop'}
```

---

## CLI report

```bash
python -m audit report usage.jsonl
```

Sample output:

```
=== LLM API Cost Audit ============================================

Rows analysed: 412   Window: 2026-09-10 08:11 -> 2026-09-16 10:22

-- Token totals by tag ---------------------------------------------
tag                 calls    prompt    completion        total
summarise             180    412,880        51,220      464,100
translate              94    128,410        19,300      147,710
...

-- Finding 1: possible retry double-billing  [HIGH] ----------------
3 task(s) called more than once inside 10s, and later calls
succeeded. Each retry likely billed a full request again.
  task_id=doc-0042  attempts=2  gap=4.1s
  task_id=doc-0107  attempts=3  gap=2.8s
  task_id=doc-0219  attempts=2  gap=7.6s
  -> Fix: make retries idempotent (see "Idempotent retries" below).

-- Finding 2: prompt_tokens variance for identical tags  [MEDIUM] ---
tag=summarise has prompt_tokens standard deviation 18.4% of mean.
Identical requests are billing differently -> cache hit/miss, or a
changing prefix. Stop estimating; track the ratio over time.

-- Finding 3: context bloat  [LOW] ---------------------------------
4 call(s) where prompt_tokens > 90% of total_tokens.
Context dominates cost. Consider trimming history or payload.
```

Exit code is `1` when any HIGH finding is present, so it can run in CI.

---

## Idempotent retries

The most expensive single bug in LLM pipelines:

```python
# ❌ double-bills on timeout: server already generated tokens
for attempt in range(3):
    try:
        resp = client.chat.completions.create(...)
        break
    except Exception:
        continue

# ✅ check before you retry
def run_once(task_id, payload):
    if already_succeeded(task_id):
        return load_result(task_id)

    resp = client.chat.completions.create(**payload)
    logger.log(resp, task_id=task_id)
    mark_succeeded(task_id, resp)
    return resp
```

The report's **Finding 1** exists to catch this after the fact.

---

## CLI reference

| Command | Purpose |
|---|---|
| `python -m audit report <log.jsonl>` | Full audit report |
| `python -m audit report <log.jsonl> --json` | Machine-readable output |
| `python -m audit report <log.jsonl> --window 600` | Retry-detection window (seconds, default 10) |
| `python -m audit tail <log.jsonl> -n 20` | Show the last N raw rows |

---

## What this tool does *not* claim

- It does **not** promise a cache hit rate. Cache behaviour depends on request shape, timing, and server policy. Track observed cost; do not assume a number.
- It does **not** compare providers or rank services.
- It does **not** read your API key or send data anywhere. Everything is local; the log file is plain JSONL that you own.

---

## Testing against a compatible endpoint

Any OpenAI-compatible `base_url` works. If you need a public endpoint to run the examples against, `https://api.91kun.top` is an OpenAI-compatible gateway with per-request usage details available in the console; model list and pricing are on the site itself. Nothing in this repository depends on it — swap in whichever endpoint you already use.

---

## License

MIT — see [LICENSE](LICENSE).
