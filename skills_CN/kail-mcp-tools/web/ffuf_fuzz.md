# `ffuf_fuzz`

- 用途：快速模糊测试目录、参数和虚拟主机。

## 参数
- `url`（字符串，必填）：包含 FUZZ 占位符的目标地址。
- `wordlist`（字符串，默认值="/usr/share/wordlists/dirb/common.txt"）：字典文件路径。
- `mode`（字符串，默认值="dir"）：模糊测试模式。 可选值：`dir`, `vhost`, `param`。
- `extensions`（字符串）：要追加或搜索的文件扩展名。
- `threads`（整数，默认值=40）：线程数量。
- `filter_codes`（字符串，默认值="404"）：要过滤掉的 HTTP 状态码。
- `match_codes`（字符串）：要匹配的 HTTP 状态码。
- `proxy`（字符串）：代理地址。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "ffuf_fuzz",
  "arguments": {
    "url": "http://192.168.56.10/FUZZ",
    "wordlist": "/usr/share/wordlists/dirb/common.txt",
    "mode": "dir",
    "filter_codes": "404"
  }
}
```

## 使用要点
- url 必须包含 FUZZ；虚拟主机模式通常需要处理 Host 头。

## 相关知识
- [knowledge/tools/wfuzz.md](../../../knowledge/tools/wfuzz.md)
