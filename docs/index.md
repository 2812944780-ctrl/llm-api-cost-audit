# LLM API Cost Audit

**Record real usage. Find hidden cost. Keep your API bill explainable.**

A small, local-first toolkit for auditing token usage from any **OpenAI-compatible** endpoint. It
catches retry double-billing, changing prompt size and context-heavy requests before they become
recurring surprises.

> Repository: <https://github.com/2812944780-ctrl/llm-api-cost-audit> ·
> [README](https://github.com/2812944780-ctrl/llm-api-cost-audit#readme) ·
> [中文说明](https://github.com/2812944780-ctrl/llm-api-cost-audit/blob/main/README.zh-CN.md)

---

## Why estimates fail

The naive formula is:

```
estimated_cost = input_chars * input_price + output_chars * output_price
```

It is structurally wrong, for four reasons:

| # | Reason | What actually happens |
|---|---|---|
| 1 | **Token ≠ characters** | Chinese, code, punctuation and emoji tokenize at very different ratios. |
| 2 | **Input is bigger than you think** | `system` prompt, history, RAG chunks and tool schemas are all billed. |
| 3 | **Caching changes the unit price** | Repeated prefixes may bill lower — *when* they hit is not something you can assume. |
| 4 | **Retries double-bill** | On timeout the server may have already generated (and billed) tokens. |

This toolkit targets #3 and #4, because they are invisible without a log.

## Install

```bash
git clone https://github.com/2812944780-ctrl/llm-api-cost-audit.git
cd llm-api-cost-audit
pip install -r requirements.txt
```

No third-party dependencies beyond the `openai` SDK.

## Quick start

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
    messages=[{"role": "user", "content": "Summarise the attached document."}],
)
print(logger.log(resp, tag="summarise", task_id="doc-0001"))
```

Then render a report:

```bash
python -m audit report usage.jsonl
```

Exit code is `1` when a `HIGH` finding is present, so it can run in CI.

## Guides

| Guide | What it covers |
|---|---|
| [Client matrix](client-matrix.md) | Which client writes which usage fields |
| [Claude Code](claude-code.md) | Configuration checks for Claude Code setups |
| [Codex CLI](codex-cli.md) | Configuration checks for Codex CLI setups |
| [CC Switch](cc-switch.md) | Switching endpoints without losing the log trail |
| [Cherry Studio](cherry-studio.md) | Cherry Studio configuration checks |
| [Streaming](streaming.md) | Usage fields in streamed responses |
| [HTTP errors](errors.md) | Troubleshooting failed requests |
| [Architecture](architecture.md) | How the logger, detectors and report fit together |
| [FAQ](faq.md) | Common questions, including what the tool will not tell you |
| [Deep Space API](using-deep-space-api.md) | Setup guide and first request |

## What this tool does *not* claim

- It does **not** promise a cache hit rate. Cache behaviour depends on request shape, timing and
  server policy. Track observed cost; do not assume a number.
- It does **not** compare providers or rank services.
- It does **not** read your API key or send data anywhere. Everything is local; the log file is plain
  JSONL that you own.

## Promotion disclosure

The setup guide is written against **Deep Space API** (`https://api.91kun.top`), which is operated by
the same maintainer as this repository. That is a commercial interest and it is disclosed here
deliberately.

Registration at Deep Space API → join the support QQ group **1041569325** → apply for **CNY 2 in API
usage credit**, once per user. Registration alone does not grant credit; never send your API key or
password to anyone. Model availability, pricing and plan limits are only authoritative on the site
itself.

**Nothing in this repository depends on that endpoint.** Every example takes a `base_url`, so you can
point it at whichever OpenAI-compatible gateway you already use.

## License

MIT — see [LICENSE](https://github.com/2812944780-ctrl/llm-api-cost-audit/blob/main/LICENSE).
