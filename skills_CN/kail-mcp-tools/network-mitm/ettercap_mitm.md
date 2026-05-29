# `ettercap_mitm`

- 用途：运行 Ettercap 中间人攻击和插件。

## 参数
- `target1`（字符串，必填）：第一个目标 IP。
- `target2`（字符串，必填）：第二个目标 IP。
- `interface`（字符串，默认值="eth0"）：网络接口。
- `attack_type`（字符串，默认值="arp"）：攻击类型。 可选值：`arp`, `dhcp`, `port`, `icmp`。
- `filters`（字符串数组）：要应用的过滤器。
- `plugins`（字符串数组）：要加载的插件。
- `mode`（字符串，默认值="text"）：界面模式。 可选值：`text`, `curses`, `daemon`。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "ettercap_mitm",
  "arguments": {
    "target1": "192.168.56.10",
    "target2": "192.168.56.1",
    "interface": "eth0",
    "attack_type": "arp",
    "mode": "text"
  }
}
```

## 使用要点
- 用于观察或改变通信路径的中间人流程。

## 相关知识
- [knowledge/tools/mitm.md](../../../knowledge/tools/mitm.md)
