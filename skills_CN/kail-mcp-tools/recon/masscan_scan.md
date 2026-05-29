# `masscan_scan`

- 用途：在大范围目标中快速发现开放的 TCP 端口。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `ports`（字符串，默认值="1-1000"）：端口说明或范围。
- `rate`（整数，默认值=1000）：每秒数据包数量。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "masscan_scan",
  "arguments": {
    "target": "192.168.56.0/24",
    "ports": "80,443,445,3389",
    "rate": 1000
  }
}
```

## 使用要点
- 用于快速发现 TCP 端口，再用 nmap_scan 确认服务。

## 相关知识
- [knowledge/tactics/recon_flow.md](../../../knowledge/tactics/recon_flow.md)
