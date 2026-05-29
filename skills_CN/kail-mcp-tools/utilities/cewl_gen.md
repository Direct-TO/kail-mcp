# `cewl_gen`

- 用途：从目标网站内容生成定制字典。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `depth`（整数，默认值=2）：爬取深度。
- `min_word_length`（整数，默认值=3）：最小词长。
- `max_word_length`（整数，默认值=20）：最大词长。
- `output_file`（字符串）：输出文件路径。
- `with_numbers`（布尔值，默认值=false）：包含数字。
- `email_addresses`（布尔值，默认值=false）：提取邮箱地址。
- `meta_data`（布尔值，默认值=false）：提取元数据。
- `user_agent`（字符串）：自定义用户代理。
- `proxy`（字符串）：代理地址。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "cewl_gen",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "depth": 1,
    "min_word_length": 5,
    "output_file": "/tmp/site-words.txt"
  }
}
```

## 使用要点
- 适合从目标网站语言中构建定制字典。

## 相关知识
- [knowledge/tools/wordlist_gen.md](../../../knowledge/tools/wordlist_gen.md)
