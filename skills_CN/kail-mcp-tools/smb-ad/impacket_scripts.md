# `impacket_scripts`

- 用途：运行 Impacket 脚本完成 Windows 或活动目录认证、枚举和执行。

## 参数
- `script`（字符串，必填）：脚本名称。 可选值：`psexec.py`, `wmiexec.py`, `smbexec.py`, `secretsdump.py`, `GetUserSPNs.py`, `GetNPUsers.py`, `ticketer.py`, `raiseChild.py`。
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `username`（字符串）：用户名或用户名文件。
- `password`（字符串）：密码或密码文件。
- `hash`（字符串）：NTLM 哈希。
- `domain`（字符串）：域名。
- `command`（字符串）：要运行的命令。
- `port`（整数）：目标端口。
- `extra_args`（字符串）：额外工具参数。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "impacket_scripts",
  "arguments": {
    "script": "GetNPUsers.py",
    "target": "dc01.example.test",
    "domain": "EXAMPLE",
    "username": "audit",
    "password": "<known-password>"
  }
}
```

## 使用要点
- 不同脚本选项不同；使用 extra_args 补充脚本专用标志。

## 相关知识
- [knowledge/tools/ad_tools.md](../../../knowledge/tools/ad_tools.md)
- [knowledge/tools/smb_advanced.md](../../../knowledge/tools/smb_advanced.md)
