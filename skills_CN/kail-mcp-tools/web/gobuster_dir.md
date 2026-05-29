# `gobuster_dir`

- 用途：使用字典发现网页目录和文件。

## 参数
- `target_url`（字符串，必填）：目标地址。
- `wordlist`（字符串，默认值="/usr/share/wordlists/dirb/common.txt"）：字典文件路径。
- `extensions`（字符串）：要追加或搜索的文件扩展名。
- `threads`（整数，默认值=10）：线程数量。
- `status_codes`（字符串）：匹配为有效的 HTTP 状态码。
- `proxy`（字符串）：代理地址。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "gobuster_dir",
  "arguments": {
    "target_url": "http://192.168.56.10",
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "extensions": "php,txt",
    "threads": 10
  }
}
```

## 使用要点
- 根据识别出的技术栈选择扩展名，例如 php、aspx 或 jsp。

## 相关知识
- [knowledge/tools/gobuster.md](../../../knowledge/tools/gobuster.md)
