# `bettercap_scan`

- 用途：运行 BetterCAP 网络发现、嗅探和中间人流程。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `gateway`（字符串）：网关 IP 地址。
- `module`（字符串，默认值="arp.spoof"）：模块名称。 可选值：`arp.spoof`, `dns.spoof`, `http.proxy`, `https.proxy`, `net.sniff`, `tcp.proxy`。
- `action`（字符串）：要执行的动作。 可选值：`scan`, `spoof`, `sniff`, `proxy`。
- `interface`（字符串）：网络接口。
- `script`（字符串）：脚本名称。
- `commands`（字符串数组）：要运行的命令列表。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "bettercap_scan",
  "arguments": {
    "target": "192.168.56.10",
    "action": "scan",
    "interface": "eth0"
  }
}
```

## 使用要点
- scan 和 sniff 用于观察流量；spoof 和 proxy 会改变流量路径。

## 相关知识
- [knowledge/tools/mitm.md](../../../knowledge/tools/mitm.md)
