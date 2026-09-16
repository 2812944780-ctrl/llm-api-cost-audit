# Claude Code 配置检查清单

这份清单只解决一个问题：**Claude Code 已经启动，但请求没有按预期到达 OpenAI 兼容端点时，先检查什么。**

## 1. 先确认端点和模型

```text
OPENAI_BASE_URL=https://your-endpoint/v1
OPENAI_API_KEY=只放在本机环境变量
OPENAI_MODEL=以端点返回的模型列表为准
```

不要把 Key 写进仓库、截图或 Issue。模型名不要凭记忆填写，先用站点或端点公开的模型列表核对。

## 2. 最小验证

先不要启动长任务，发送一条短消息，记录：

- HTTP 状态码；
- 响应中的 `model`；
- `usage.prompt_tokens`、`usage.completion_tokens`、`usage.total_tokens`；
- `finish_reason`；
- 本地时间、首包时间和总耗时。

本仓库的 `UsageLogger` 可以把响应里的 usage 写入 JSONL，之后运行：

```bash
python -m audit report usage.jsonl
```

## 3. 常见状态码

| 状态码 | 先检查 |
|---|---|
| 401 | Key 是否属于当前端点、Authorization 是否被客户端覆盖 |
| 402 | 余额、套餐额度或钱包续用开关；不要重复重试 |
| 404 | Base URL 是否多写/少写 `/v1`，模型名是否存在 |
| 429 | 并发、限流和重试退避；为任务设置唯一 `task_id` |

## 4. 配置改了但仍走旧端点

完全退出 Claude Code 和相关终端进程，再重新打开。然后用一条最小请求检查返回的 `model` 和服务端用量，不要只看客户端界面上的供应商名称。

## 5. 账单核对

客户端日志、响应 `usage` 和服务端用量明细要按同一个请求时间或请求 ID 对照。缓存命中率不要预设固定数字；只记录实际观察结果。
