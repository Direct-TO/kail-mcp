# `netcat_connect`

- 用途：建立 TCP 连接、监听器和轻量横幅检查。

## 参数
- `target`（字符串）：目标主机、IP、范围或域名，具体含义取决于工具。
- `port`（整数，必填）：目标端口。
- `mode`（字符串，默认值="connect"）：连接模式。 可选值：`connect`, `listen`。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "netcat_connect",
  "arguments": {
    "target": "192.168.56.10",
    "port": 80,
    "mode": "connect",
    "extra_args": "-w 3"
  }
}
```

## 相关知识
- [knowledge/tools/netcat.md](../../../knowledge/tools/netcat.md)
