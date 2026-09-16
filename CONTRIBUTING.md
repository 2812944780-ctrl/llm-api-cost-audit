# Contributing

感谢贡献。这个项目优先接受可复现的 API 兼容性、usage 记录和成本排查改进。

## 提交前检查

```bash
python -m compileall -q audit examples
python -m audit report sample-usage.jsonl --json
```

报告包含 HIGH 级发现时返回码为 1，这是设计行为；它表示样例命中了重复调用检测，不代表命令崩溃。

## 安全要求

- 不提交 API Key、Token、Cookie、Authorization、真实账单或用户提示词；
- 示例使用占位符和环境变量；
- 不提交 `usage.jsonl`、`.env` 或包含真实请求数据的日志；
- 不把项目改成服务商排名或未经验证的稳定性承诺。

## Issue 内容

请提供脱敏后的：HTTP 状态码、模型名、端点协议、usage 形状和复现步骤。不要粘贴凭据或完整私有上下文。也可以使用仓库内的 Bug Report / Feature Request 模板。

## 文档贡献

文档应优先解决一个可复现的问题，避免未经验证的稳定性、价格、缓存命中率或模型可用性承诺。涉及某个接口时，请把当天会变化的价格和模型列表写成“以站内当前页面为准”。
