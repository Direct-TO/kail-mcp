# `nmap_scan`

- 用途：使用 Nmap 做主机发现、端口扫描、服务识别和脚本扫描。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `scan_type`（字符串，默认值="quick"）：Nmap 扫描配置。 可选值：`quick`, `full`, `stealth`, `vuln`, `scripts`, `discovery`, `udp`。
- `ports`（字符串）：端口说明或范围。
- `timing`（字符串，默认值="T3"）：时间模板。 可选值：`T0`, `T1`, `T2`, `T3`, `T4`, `T5`。
- `scripts`（字符串）：要运行的 NSE 脚本。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "nmap_scan",
  "arguments": {
    "target": "192.168.56.10",
    "scan_type": "quick",
    "timing": "T3"
  }
}
```

## 使用要点
- 对网段先使用 discovery，再对存活主机做端口扫描。
- extra_args 只放配置参数未覆盖的标志。

## 相关知识
- [knowledge/tools/nmap.md](../../../knowledge/tools/nmap.md)
