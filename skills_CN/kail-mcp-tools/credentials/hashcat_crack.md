# `hashcat_crack`

- 用途：使用 Hashcat 离线破解密码哈希。

## 参数
- `hash_file`（字符串，必填）：包含哈希的文件。
- `hash_type`（整数，必填）：Hashcat 哈希类型代码。
- `wordlist`（字符串，必填）：字典文件路径。
- `rules`（字符串）：Hashcat 规则文件路径。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "hashcat_crack",
  "arguments": {
    "hash_file": "/tmp/hashes.txt",
    "hash_type": 0,
    "wordlist": "/usr/share/wordlists/rockyou.txt"
  }
}
```

## 使用要点
- 先识别 hash_type；错误模式会浪费时间。

## 相关知识
- [knowledge/tools/hashcat.md](../../../knowledge/tools/hashcat.md)
