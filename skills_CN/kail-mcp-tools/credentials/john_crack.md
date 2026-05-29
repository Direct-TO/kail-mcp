# `john_crack`

- 用途：使用 John the Ripper 离线破解密码哈希并识别格式。

## 参数
- `hash_file`（字符串，必填）：包含哈希的文件。
- `wordlist`（字符串）：字典文件路径。
- `format`（字符串）：John 哈希格式。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "john_crack",
  "arguments": {
    "hash_file": "/tmp/hashes.txt",
    "wordlist": "/usr/share/wordlists/rockyou.txt",
    "format": "raw-md5"
  }
}
```

## 使用要点
- 格式不确定时先让 John 自动识别，再按需要补充 format。

## 相关知识
- [knowledge/tools/john.md](../../../knowledge/tools/john.md)
