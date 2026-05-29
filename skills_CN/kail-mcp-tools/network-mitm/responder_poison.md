# `responder_poison`

- 用途：运行 Responder 分析或名称解析投毒。

## 参数
- `interface`（字符串，必填，默认值="eth0"）：网络接口。
- `mode`（字符串，默认值="poison"）：Responder 模式。 可选值：`analyze`, `poison`。
- `services`（字符串数组）：要启用的服务。
- `wpad`（布尔值，默认值=true）：启用网页代理自动发现服务行为。
- `fingerprint`（布尔值，默认值=true）：启用指纹识别。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "responder_poison",
  "arguments": {
    "interface": "eth0",
    "mode": "analyze",
    "wpad": false,
    "fingerprint": true
  }
}
```

## 使用要点
- analyze 模式观察流量；poison 模式执行投毒。

## 相关知识
- [knowledge/tools/mitm.md](../../../knowledge/tools/mitm.md)
