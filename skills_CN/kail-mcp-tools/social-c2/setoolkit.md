# `setoolkit`

- 用途：运行 Social Engineering Toolkit 工作流。

## 参数
- `attack_vector`（整数，必填）：攻击向量选择。 可选值：`1`, `2`, `3`, `4`, `5`。
- `web_attack_type`（整数）：网页攻击类型选择。 可选值：`1`, `2`, `3`, `4`。
- `clone_url`（字符串）：要克隆的地址。
- `payload`（字符串）：载荷名称。
- `lhost`（字符串）：监听主机 IP。
- `lport`（整数）：监听端口。
- `email_template`（字符串）：邮件模板。
- `target_email`（字符串）：目标邮箱地址。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "setoolkit",
  "arguments": {
    "attack_vector": 2,
    "web_attack_type": 3,
    "clone_url": "http://192.168.56.10"
  }
}
```

## 使用要点
- 支持邮件、克隆页面和凭据收集流程。

## 相关知识
- [knowledge/tools/social_engineering.md](../../../knowledge/tools/social_engineering.md)
