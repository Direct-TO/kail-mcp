# `medusa_bruteforce`

- 用途：使用 Medusa 做并行在线口令猜测。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `service`（字符串，必填）：目标服务。 可选值：`ssh`, `ftp`, `telnet`, `http`, `pop3`, `imap`, `smb`, `mysql`, `mssql`, `postgres`。
- `username`（字符串）：用户名或用户名文件。
- `user_list`（字符串）：用户名列表路径。
- `password_list`（字符串，必填）：密码列表路径。
- `port`（整数）：目标端口。
- `threads`（整数，默认值=5）：线程数量。
- `timeout`（整数，默认值=10）：超时时间，单位为秒。
- `verbose`（布尔值，默认值=false）：详细输出。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "medusa_bruteforce",
  "arguments": {
    "target": "192.168.56.10",
    "service": "ssh",
    "username": "test",
    "password_list": "/usr/share/wordlists/rockyou.txt",
    "threads": 2
  }
}
```

## 使用要点
- 类似 hydra_attack，适合并行尝试。

## 相关知识
- [knowledge/tools/brute_alt.md](../../../knowledge/tools/brute_alt.md)
