# Security Policy

## Supported scope

安全问题包括：密钥泄露、日志中的隐私数据、认证头处理、危险的默认配置，以及会导致错误计费判断的安全缺陷。

## Report privately

请不要在公开 Issue 中粘贴 API Key、Cookie、Authorization、真实账单、用户提示词或完整生产响应。先删除敏感字段，再通过 GitHub Security advisory 或仓库维护者的私下渠道报告。

报告请包含：

- 受影响的文件和版本；
- 脱敏后的复现步骤；
- 可能的影响；
- 不包含凭据的日志片段。

## Local data handling

`usage.jsonl` 可能包含模型名、任务 ID、时间和 Token 用量。它默认只保存在本地，提交前请确认没有真实业务数据。仓库的 `.gitignore` 已忽略常见日志和环境文件，但提交前仍应人工检查。
