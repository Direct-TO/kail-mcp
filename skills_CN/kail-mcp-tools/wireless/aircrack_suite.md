# `aircrack_suite`

- 用途：运行 Aircrack-ng 的监听、抓包、注入和破解流程。

## 参数
- `command`（字符串，必填）：要运行的命令。 可选值：`airodump`, `aireplay`, `aircrack`, `airmon`, `packetforge`。
- `interface`（字符串）：网络接口。
- `bssid`（字符串）：目标基本服务集标识符。
- `channel`（整数）：目标信道。
- `essid`（字符串）：目标扩展服务集标识符。
- `capture_file`（字符串）：捕获文件路径。
- `wordlist`（字符串）：字典文件路径。
- `attack_type`（字符串）：攻击类型。 可选值：`deauth`, `arp`, `fragment`, `cafe`。
- `client`（字符串）：关联客户端 MAC 地址。
- `output_prefix`（字符串）：输出文件名前缀。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "aircrack_suite",
  "arguments": {
    "command": "airodump",
    "interface": "wlan0mon",
    "output_prefix": "/tmp/wifi-audit"
  }
}
```

## 使用要点
- 需要无线网卡和监听模式。

## 相关知识
- [knowledge/tools/wireless.md](../../../knowledge/tools/wireless.md)
