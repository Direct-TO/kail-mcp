# `auto_recon`

- 用途：自动串联 whois、dig、nmap、whatweb 和 gobuster 做初始侦察。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `ports`（字符串）：端口说明或范围。
- `web_ports`（字符串）：需要检查网页服务的端口。
- `wordlist`（字符串，默认值="/usr/share/wordlists/dirb/common.txt"）：字典文件路径。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "auto_recon",
  "arguments": {
    "target": "192.168.56.10",
    "ports": "80,443,8080",
    "web_ports": "80,443",
    "wordlist": "/usr/share/wordlists/dirb/common.txt"
  }
}
```

## 使用要点
- 用于第一轮摸底；目标较大时手动设置 ports 和 web_ports。

## 相关知识
- [knowledge/tactics/recon_flow.md](../../../knowledge/tactics/recon_flow.md)
