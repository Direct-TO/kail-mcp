# `wfuzz_scan`

- 用途：对路径、参数、虚拟主机和其他网页输入进行模糊测试。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `wordlist`（字符串，必填）：字典文件路径。
- `hide_codes`（字符串）：要隐藏的响应状态码。
- `hide_chars`（字符串）：要隐藏的字符数量。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "wfuzz_scan",
  "arguments": {
    "target_url": "http://192.168.56.10/FUZZ",
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "hide_codes": "404"
  }
}
```

## 使用要点
- target_url 必须包含 FUZZ；先隐藏明显的 404 或 302 噪声。

## 相关知识
- [knowledge/tools/wfuzz.md](../../../knowledge/tools/wfuzz.md)
