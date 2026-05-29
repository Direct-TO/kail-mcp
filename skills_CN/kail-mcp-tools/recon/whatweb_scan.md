# `whatweb_scan`

- 用途：识别网页技术栈和应用指纹。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `aggression`（字符串，默认值="1"）：WhatWeb 强度级别。 可选值：`1`, `3`, `4`。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "whatweb_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "aggression": "1"
  }
}
```

## 相关知识
- [knowledge/tools/whatweb.md](../../../knowledge/tools/whatweb.md)
