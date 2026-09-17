# 使用深空 API 做 OpenAI 兼容接口回归

这是一份**配置和核对指南**，不是服务商排名。目标是让你在 Claude Code、Codex、CC Switch 或自己的脚本里，先完成一次最小请求，再决定是否继续使用。

## GitHub 用户领取 2 元额度

1. 打开 [深空 API 官网](https://api.91kun.top) 注册，记下自己的站内用户 ID 或昵称。
2. 加入售后 QQ 群 **1041569325**，入群申请填写：`GitHub + 站内用户ID或昵称`。
3. 在售后群申请领取 **2 元站内 API 使用额度，每个用户限领一次**。不是注册自动到账，不要在申请中提供 API Key 或密码。
4. 额度发放后，在站内创建 API Key，复制当天可用的模型 ID，按下面的示例完成一次最小调用，再对照站内用量明细。

## 接入信息

```text
Base URL: https://api.91kun.top/v1
API Key: 只通过本机环境变量或客户端安全配置保存
Model: 以模型广场当天公开的模型 ID 为准
```

模型、价格、分组、状态、限制和套餐以站内当天页面为准。不要把模型名从旧截图或旧文章里照抄过来。

## 先做最小请求

Windows PowerShell：

```powershell
$env:OPENAI_BASE_URL = "https://api.91kun.top/v1"
$env:OPENAI_API_KEY = "替换为你自己的 Key"
$env:OPENAI_MODEL = "替换为当天页面中的模型 ID"

./examples/curl/chat-completion.ps1
```

Linux/macOS：

```bash
export OPENAI_BASE_URL=https://api.91kun.top/v1
export OPENAI_API_KEY='替换为你自己的 Key'
export OPENAI_MODEL='替换为当天页面中的模型 ID'

bash examples/curl/chat-completion.sh
```

请求成功后，至少检查响应里的：

```text
HTTP status
model
usage.prompt_tokens
usage.completion_tokens
usage.total_tokens
finish_reason
```

## Python SDK

```python
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ.get("OPENAI_BASE_URL", "https://api.91kun.top/v1"),
)

response = client.chat.completions.create(
    model=os.environ["OPENAI_MODEL"],
    messages=[{"role": "user", "content": "Reply with one short sentence."}],
)

print(response.model)
print(response.usage)
print(response.choices[0].finish_reason)
```

需要记录长期用量时，配合本仓库的 `UsageLogger`：

```bash
python examples/basic_usage.py
python -m audit report usage.jsonl
```

## 三种付费方式的核对思路

- **按量余额**：适合用量不确定的请求；按量余额最低充值和当前倍率以当天站内页面为准。
- **日卡**：适合一天集中使用；查看套餐额度、24 小时有效期、支持分组和并发限制。
- **周卡**：适合连续几天使用；查看每日额度、刷新周期、未使用额度是否累计以及到期规则。

套餐不是无限量。套餐额度优先使用；额度用完后是否继续扣钱包余额，以用户主动开启的设置和当天页面规则为准。GitHub 来源用户可按上方步骤申请一次 2 元额度，不代表套餐无限量或注册自动赠送。

## 账单核对

把本地日志和站内用量明细按以下字段对照：

```text
请求时间
response.model
usage
finish_reason
请求 ID（如果返回）
实际扣费明细
```

缓存命中率不做固定承诺。相同标签的 `prompt_tokens` 出现波动时，先记录实际请求形状和账单，不要直接认定为异常。

## 安全提醒

- 不把 API Key 写入代码、README、截图、Issue 或提交记录；
- 不提交 `usage.jsonl`、真实用户提示词和完整响应；
- 分享错误时只保留脱敏后的状态码、模型名、usage 形状和重试信息；
- 不要因为一次超时就无条件重试，服务端可能已经产生用量。

## 入口

- 官网与当天模型/价格/套餐页面：<https://api.91kun.top>
- API 文档：<https://api.91kun.top/docs>
- 本仓库的 [错误码排查](errors.md)、[流式排错](streaming.md)、[Claude Code 清单](claude-code.md)、[Codex CLI 清单](codex-cli.md)
