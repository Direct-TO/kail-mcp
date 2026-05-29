# `wifite_audit`

- 用途：使用 Wifite 做自动化无线审计。

## 参数
- `interface`（字符串，必填，默认值="wlan0"）：网络接口。
- `target_bssid`（字符串）：指定目标基本服务集标识符。
- `target_channel`（整数）：指定目标信道。
- `attack`（字符串，默认值="wpa"）：攻击类型。 可选值：`wep`, `wpa`, `wps`。
- `wordlist`（字符串）：字典文件路径。
- `wps_pin`（布尔值，默认值=true）：尝试 WPS PIN 攻击。
- `no_wps`（布尔值，默认值=false）：禁用 WPS 攻击。
- `power`（整数，默认值=-80）：最低信号强度。
- `clients`（布尔值，默认值=true）：显示已连接客户端。
- `wep_attack`（字符串）：指定 WEP 攻击。 可选值：`arp`, `chopchop`, `fragment`。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "wifite_audit",
  "arguments": {
    "interface": "wlan0",
    "attack": "wpa",
    "no_wps": true,
    "power": -70
  }
}
```

## 使用要点
- 使用 BSSID 和 channel 过滤目标选择。

## 相关知识
- [knowledge/tools/wireless.md](../../../knowledge/tools/wireless.md)
