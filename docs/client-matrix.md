# 客户端接入矩阵

所有客户端都建议先发一条短请求，再核对响应中的 `model`、`usage` 和 `finish_reason`。

| 客户端 | 协议入口 | 关键配置 | 首次验证 |
|---|---|---|---|
| Python SDK | Chat Completions | `api_key`、`base_url`、`model` | 运行 `examples/basic_usage.py` |
| Node.js | Chat Completions | 环境变量、原生 `fetch` | 运行 `examples/nodejs/chat-completion.mjs` |
| curl | Chat Completions | `OPENAI_BASE_URL`、`OPENAI_API_KEY`、`OPENAI_MODEL` | 运行 shell 示例 |
| PowerShell | Chat Completions | 同上 | 运行 `.ps1` 示例 |
| Claude Code | 以客户端版本为准 | endpoint、Key、模型映射 | 发一条最小任务并查实际模型 |
| Codex CLI | 以客户端版本为准 | `base_url`、Key、模型 ID | 检查 Responses / Chat 路径 |
| CC Switch | OpenAI 兼容配置 | 供应商、Base URL、Key、模型 | 退出旧进程后重新启动 |
| Cherry Studio | OpenAI Compatible | Base URL、Key、模型 ID | 新建短对话并查用量 |

## 判断接入是否真的生效

只看客户端下拉框或供应商名称不够。至少同时记录：

```text
实际请求地址
响应 model
HTTP status
usage
finish_reason
请求 ID（如果有）
```

如果客户端没有展示这些字段，可以用本仓库的 curl 或 Python 标准库示例做旁路验证。

## 协议差异

OpenAI 兼容不等于所有接口细节完全相同。尤其要核对：

- Chat Completions 与 Responses 的路径是否一致；
- 流式事件格式是否符合客户端预期；
- `tool_calls`、JSON schema 和 reasoning 字段是否被支持；
- 客户端是否自动改写模型名或 Base URL。

遇到 401、402、404、429，先看 [错误码排查](errors.md)，不要无条件更换所有配置。
