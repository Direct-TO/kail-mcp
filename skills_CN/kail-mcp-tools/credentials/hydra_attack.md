# `hydra_attack`

- 用途：使用 Hydra 做在线口令猜测或密码喷洒。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `service`（字符串，必填）：目标服务。 可选值：`ssh`, `ftp`, `http-get`, `http-post`, `http-post-form`, `smb`, `rdp`, `mysql`, `mssql`, `postgres`, `vnc`, `telnet`, `smtp`, `pop3`, `imap`。
- `port`（整数）：目标端口。
- `username`（字符串）：用户名或用户名文件。
- `username_list`（字符串）：用户名列表路径。
- `password_list`（字符串，必填）：密码列表路径。
- `threads`（整数，默认值=4）：线程数量。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "hydra_attack",
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
- 使用 threads 控制并发；也支持密码喷洒。

## 相关知识
- [knowledge/tools/hydra.md](../../../knowledge/tools/hydra.md)
