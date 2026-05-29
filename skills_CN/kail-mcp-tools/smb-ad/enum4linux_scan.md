# `enum4linux_scan`

- 用途：枚举文件共享和网络基本输入输出系统中的用户、共享、组和策略。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `options`（字符串，默认值="all"）：模块选项。 可选值：`all`, `users`, `shares`, `policies`, `groups`。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "enum4linux_scan",
  "arguments": {
    "target": "192.168.56.10",
    "options": "all"
  }
}
```

## 使用要点
- 常用于初始文件共享枚举，再进入凭据测试。

## 相关知识
- [knowledge/tools/enum4linux.md](../../../knowledge/tools/enum4linux.md)
