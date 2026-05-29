# `crunch_gen`

- 用途：按长度、字符集或模式生成字典。

## 参数
- `min_length`（整数，必填）：最小长度。
- `max_length`（整数，必填）：最大长度。
- `charset`（字符串）：字符集。
- `pattern`（字符串）：生成模式。
- `output_file`（字符串）：输出文件路径。
- `start_string`（字符串）：起始字符串。
- `stop_string`（字符串）：停止字符串。
- `compress`（布尔值，默认值=false）：压缩输出。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "crunch_gen",
  "arguments": {
    "min_length": 8,
    "max_length": 8,
    "charset": "abc123",
    "output_file": "/tmp/custom-wordlist.txt"
  }
}
```

## 使用要点
- 控制长度和字符集，避免输出文件过大。

## 相关知识
- [knowledge/tools/wordlist_gen.md](../../../knowledge/tools/wordlist_gen.md)
