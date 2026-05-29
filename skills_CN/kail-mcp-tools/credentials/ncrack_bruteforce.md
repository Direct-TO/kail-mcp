# `ncrack_bruteforce`

- 用途：使用 Ncrack 做高速网络认证破解。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `service`（字符串，必填）：目标服务。 可选值：`ssh`, `rdp`, `ftp`, `telnet`, `http`, `https`, `smb`, `mysql`, `vnc`。
- `user_list`（字符串，必填）：用户名列表路径。
- `pass_list`（字符串，必填）：密码列表路径。
- `timing`（字符串，默认值="T3"）：时间模板。 可选值：`T0`, `T1`, `T2`, `T3`, `T4`, `T5`。
- `port`（整数）：目标端口。
- `connections`（整数，默认值=5）：参数值。
- `save`（字符串）：保存结果的文件路径。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "ncrack_bruteforce",
  "arguments": {
    "target": "192.168.56.10:22",
    "service": "ssh",
    "user_list": "/tmp/users.txt",
    "pass_list": "/tmp/passwords.txt",
    "timing": "T2",
    "connections": 2
  }
}
```

## 使用要点
- 这是高速工具；需要有意识地调整 timing 和 connections。

## 相关知识
- [knowledge/tools/brute_alt.md](../../../knowledge/tools/brute_alt.md)
