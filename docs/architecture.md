# Architecture

本项目故意保持小型：调用逻辑由你的客户端负责，审计层只接收响应并写入本地 JSONL。

```text
OpenAI-compatible client
          |
          v
      API response
          |
          v
   audit.UsageLogger
          |
          v
      usage.jsonl
          |
          v
   audit report / tail
          |
          v
 retry / variance / context findings
```

## 模块职责

- `audit/logger.py`：提取响应中的模型、Token、结束原因、请求 ID和业务标签；
- `audit/report.py`：执行三个独立检测器；
- `audit/cli.py`：提供 `report` 和 `tail` 命令；
- `examples/`：提供 SDK、标准库、Node.js、curl 和 PowerShell 调用方式；
- `docs/`：记录客户端配置和排错边界。

## 数据边界

审计工具只在本地写 JSONL，不上传数据。调用端仍可能把提示词发送给你选择的接口，因此不要把密钥、隐私内容或完整生产日志提交到 GitHub。

## 扩展检测器

新增检测器时，优先遵循：

1. 输入来自已经记录的字段；
2. 结果可以用样例日志复现；
3. 结论使用“可能”“观察到”等准确措辞，不把启发式判断写成账单事实；
4. HIGH 级别只用于可能导致重复扣费或数据损失的明确风险。
