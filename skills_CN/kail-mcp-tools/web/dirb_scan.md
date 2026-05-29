# `dirb_scan`

- 用途：使用 DIRB 发现网页内容。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `wordlist`（字符串，默认值="/usr/share/wordlists/dirb/common.txt"）：字典文件路径。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "dirb_scan",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "wordlist": "/usr/share/wordlists/dirb/common.txt"
  }
}
```

## 相关知识
- [knowledge/tools/dirb.md](../../../knowledge/tools/dirb.md)
