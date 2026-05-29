# `crackmapexec`

- 用途：在 Windows 或活动目录网络中验证凭据、枚举并运行模块。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `protocol`（字符串，默认值="smb"）：使用的协议。 可选值：`smb`, `ssh`, `winrm`, `mssql`, `ldap`, `ftp`。
- `username`（字符串）：用户名或用户名文件。
- `password`（字符串）：密码或密码文件。
- `hash`（字符串）：NTLM 哈希。
- `module`（字符串）：模块名称。
- `command`（字符串）：要运行的命令。
- `exec_method`（字符串）：执行方法。 可选值：`wmiexec`, `smbexec`, `atexec`, `psexec`。
- `port`（整数）：目标端口。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "crackmapexec",
  "arguments": {
    "target": "192.168.56.10",
    "protocol": "smb",
    "username": "audit",
    "password": "<known-password>"
  }
}
```

## 使用要点
- 可验证凭据、枚举、执行命令、转储数据和运行模块。

## 相关知识
- [knowledge/tools/ad_tools.md](../../../knowledge/tools/ad_tools.md)
