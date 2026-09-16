# LLM API 成本审计

> 记录真实用量，定位隐性成本，让 API 账单可以解释。

一个小型、本地优先的 **OpenAI 兼容接口**用量审计工具。它能发现重复重试、提示词大小漂移和上下文膨胀，避免成本问题长期积累。

[![CI](https://github.com/2812944780-ctrl/llm-api-cost-audit/actions/workflows/checks.yml/badge.svg)](https://github.com/2812944780-ctrl/llm-api-cost-audit/actions/workflows/checks.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English →](README.md) · [深空 API 接入](docs/using-deep-space-api.md) · [客户端矩阵](docs/client-matrix.md) · [FAQ](docs/faq.md) · [架构](docs/architecture.md)

> 本仓库不提供免费额度或试用额度。请使用你已经信任的接口；选择付费方案前，先核对当天价格、限制和计费规则。

---

## 为什么"字数 × 单价"永远算不准

```
预估花费 = 输入字数 × 输入单价 + 输出字数 × 输出单价
```

这个公式在结构上就是错的，四个原因：

| # | 原因 | 实际情况 |
|---|---|---|
| 1 | **token ≠ 字数** | 中文、代码、标点、emoji 的换算比例完全不同，用字数反推必然漂移 |
| 2 | **输入比你想象的大** | `system` prompt、历史上下文、RAG 片段、工具定义**全部计费**，通常比用户那句话大一个数量级 |
| 3 | **缓存会改变实际单价** | 重复前缀可能按更低单价计费——但**什么时候命中，不是你能假设的** |
| 4 | **重试会重复计费** | 超时时服务端可能已经开始生成并计费，你的重试等于再付一次 |

本工具直接针对 **#3 和 #4**——因为这两个问题在没有日志的情况下是看不见的。

---

## 安装

```bash
git clone https://github.com/2812944780-ctrl/llm-api-cost-audit.git
cd llm-api-cost-audit
pip install -r requirements.txt
```

除 `openai` SDK 外无第三方依赖。

## 包含什么

| 领域 | 内容 |
|---|---|
| 记录 | model、输入/输出/总 Token、finish reason、请求 ID、标签 |
| 检测 | 重试重复计费、prompt Token 波动、上下文膨胀 |
| 运行 | Python SDK、Python 标准库、Node.js 18+、curl、PowerShell |
| 配置 | Claude Code、Codex CLI、CC Switch、Cherry Studio |
| 运维 | CLI 报告、JSON 输出、CI 卡口、脱敏 Issue 模板 |

## 示例与文档

- Python SDK：`examples/basic_usage.py`
- Python 标准库：`examples/python/chat_completion.py`
- Node.js 18+：`examples/nodejs/chat-completion.mjs`
- Linux/macOS curl：`examples/curl/chat-completion.sh`
- Windows PowerShell：`examples/curl/chat-completion.ps1`
- 环境变量模板：`examples/configs/`
- [深空 API 接入](docs/using-deep-space-api.md)
- [客户端矩阵](docs/client-matrix.md)
- [Claude Code 配置检查](docs/claude-code.md)
- [Codex CLI 配置检查](docs/codex-cli.md)
- [CC Switch 配置检查](docs/cc-switch.md)
- [Cherry Studio 配置检查](docs/cherry-studio.md)
- [HTTP 错误排查](docs/errors.md)
- [流式响应排错](docs/streaming.md)
- [FAQ](docs/faq.md)
- [架构说明](docs/architecture.md)

所有示例都从环境变量读取凭据，不会把 Key 写入文件。

---

## 快速开始

用 `UsageLogger` 包住任意一次调用：

```python
import os
from openai import OpenAI
from audit import UsageLogger

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://your-endpoint/v1",   # 任意 OpenAI 兼容端点
)
logger = UsageLogger("usage.jsonl")

resp = client.chat.completions.create(
    model="your-model-name",
    messages=[
        {"role": "system", "content": "你是一个严谨的技术助手。"},
        {"role": "user", "content": "把下面这段文本翻译成英文。"},
    ],
)

print(logger.log(resp, tag="translate", task_id="doc-0001"))
```

```
{'ts': '2026-09-16T10:22:41+00:00', 'tag': 'translate', 'task_id': 'doc-0001',
 'model': '...', 'prompt_tokens': 1284, 'completion_tokens': 396,
 'total_tokens': 1680, 'finish_reason': 'stop'}
```

**不想申请 API Key 也能先看效果**（用内置的样例日志）：

```bash
python examples/make_sample_log.py
python -m audit report sample-usage.jsonl
```

---

## 命令行报告

```bash
python -m audit report usage.jsonl
```

输出示例：

```
-- Token totals by tag ----------------------------------------
tag                    calls      prompt  completion       total
summarise                 45      56,931      15,825      72,756
rag-answer                 6      64,183       1,883      66,066
translate                 25       5,565       3,103       8,668

-- Finding 1: retry-double-billing  [HIGH] ----------
2 task(s) were called more than once inside 10s.
  task_id=doc-0042 attempts=2 gap=4.0s tokens=3366
  task_id=doc-0107 attempts=3 gap=2.0s tokens=3391
  -> 给每个任务打唯一 ID，重试前先检查它是否已经成功过。

-- Finding 2: prompt-token-variance  [MEDIUM] ----------
tag=summarise samples=45 mean=1265 stdev=96 spread=7.6%
  -> 别按固定单价算，记录每次实际扣费看趋势。

-- Finding 3: context-bloat  [LOW] ----------
6 call(s) spent >= 90% of their tokens on input.
  -> 先去精简上下文，再考虑换更便宜的端点。
```

**有 HIGH 级别问题时进程返回码为 1**，可以直接接进 CI 做卡口。

### 三个检测器分别在查什么

| 检测器 | 判据 | 说明 |
|---|---|---|
| `retry-double-billing` | 同一 `task_id` 在 N 秒内被调用多次 | 超时重试最常见的钱坑 |
| `prompt-token-variance` | 同一 tag 的 `prompt_tokens` 波动明显 | 提示缓存命中/未命中，或前缀在变 |
| `context-bloat` | `prompt_tokens` 占 `total_tokens` ≥ 90% | 输入就是账单，先削上下文再换端点 |

---

## 幂等重试：最贵的一个 bug

```python
# ❌ 超时会重复计费：服务端其实已经生成了 token
for attempt in range(3):
    try:
        resp = client.chat.completions.create(...)
        break
    except Exception:
        continue

# ✅ 重试前先检查
def run_once(task_id, payload):
    if already_succeeded(task_id):
        return load_result(task_id)

    resp = client.chat.completions.create(**payload)
    logger.log(resp, task_id=task_id)
    mark_succeeded(task_id, resp)
    return resp
```

报告里的 **Finding 1** 就是用来事后抓这个问题的。

---

## 命令行参考

| 命令 | 用途 |
|---|---|
| `python -m audit report <log.jsonl>` | 完整审计报告 |
| `python -m audit report <log.jsonl> --json` | 机器可读输出 |
| `python -m audit report <log.jsonl> --window 600` | 重试检测窗口（秒，默认 10） |
| `python -m audit tail <log.jsonl> -n 20` | 查看最近 N 行原始记录 |

---

## 这个工具**不**做什么

- **不**承诺任何缓存命中率。缓存取决于请求构造、时间间隔和服务端策略，**没有任何一方能替你保证**。请记录实际扣费，不要假设一个数字。
- **不**比较服务商、**不**给站点排名。
- **不**读取你的 API Key、**不**上传任何数据。全部在本地运行，日志是你自己的普通 JSONL 文件。

---

## 用兼容端点测试

任何 OpenAI 兼容的 `base_url` 都能用。如果你需要一个现成端点来跑示例，`https://api.91kun.top` 是一个 OpenAI 兼容网关，控制台里可以查到每笔请求的用量明细；模型列表与价格以站内当天页面为准。**本仓库不依赖任何特定端点**，换成你正在用的那个即可。

---

## 许可证

MIT — 见 [LICENSE](LICENSE)。
