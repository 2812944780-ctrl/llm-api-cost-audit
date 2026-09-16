# Codex CLI / OpenAI 兼容端点检查清单

这份清单用于排查 Codex CLI 配置后出现的 401、404、429 或模型不一致。

## 配置原则

- `base_url`、API Key、模型名分别核对，不要把三者混成一个“供应商配置”；
- Key 只通过本机环境变量或客户端的安全配置保存；
- 模型名以当前端点返回的模型列表为准；
- 先跑一条短请求，再开始长任务。

## 最小回归记录

每次更换端点后，至少保存：

```text
endpoint
model
HTTP status
response.model
usage.prompt_tokens
usage.completion_tokens
usage.total_tokens
finish_reason
首包耗时 / 总耗时
```

如果客户端支持 Responses API，而你的端点只实现 Chat Completions，必须先确认协议兼容范围，不要仅凭“OpenAI 兼容”四个字判断所有功能都可用。

## 错误定位

- `401`：检查 Key 是否发给了正确的 Base URL；
- `402`：检查按量余额、套餐额度和是否允许额度用尽后扣钱包；
- `404`：检查路径拼接和模型 ID；
- `429`：降低并发，记录重试次数，并给每个任务使用稳定的唯一 ID。

## 切换后仍出现旧模型

完全退出 Codex CLI 进程后重新启动。用响应里的 `model` 字段确认真实路由，不以本地配置文件名或 UI 标签作为证据。

## 与本仓库配合

如果你通过兼容的 Chat Completions 端点进行测试，可以使用 `examples/basic_usage.py` 记录 usage，再用：

```bash
python -m audit report usage.jsonl
```

本工具只分析本地日志，不比较服务商，也不承诺缓存命中率。
