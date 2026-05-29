---
name: kail-mcp-tools
description: 用于选择或调用 kail-mcp 渗透测试工具；包含简明用途、参数和示例。
---

# kail-mcp 工具

需要选择、编排或调用 kail-mcp 工具时使用这个技能。

## 使用方法
1. 从下面的目录选择工具。
2. 打开对应工具页，查看参数和最小 MCP 调用示例。
3. 需要查看历史结果时用 `get_scan_history`；需要生成 Markdown 报告时用 `generate_report`。

## 工具目录

### 侦察

| 工具 | 用途 | 页面 |
|---|---|---|
| `auto_recon` | 自动串联 whois、dig、nmap、whatweb 和 gobuster 做初始侦察。 | [recon/auto_recon.md](recon/auto_recon.md) |
| `nmap_scan` | 使用 Nmap 做主机发现、端口扫描、服务识别和脚本扫描。 | [recon/nmap_scan.md](recon/nmap_scan.md) |
| `masscan_scan` | 在大范围目标中快速发现开放的 TCP 端口。 | [recon/masscan_scan.md](recon/masscan_scan.md) |
| `whois_lookup` | 查询域名或 IP 的注册信息。 | [recon/whois_lookup.md](recon/whois_lookup.md) |
| `dig_lookup` | 查询 DNS 记录和解析器。 | [recon/dig_lookup.md](recon/dig_lookup.md) |
| `theharvester_recon` | 收集邮箱、子域、主机名和人员名称。 | [recon/theharvester_recon.md](recon/theharvester_recon.md) |
| `whatweb_scan` | 识别网页技术栈和应用指纹。 | [recon/whatweb_scan.md](recon/whatweb_scan.md) |
| `searchsploit_query` | 在本地 Exploit-DB 索引中搜索公开利用参考。 | [recon/searchsploit_query.md](recon/searchsploit_query.md) |
| `cve_lookup` | 按编号、关键词、通用平台枚举、严重度或日期查询 NVD 漏洞数据。 | [recon/cve_lookup.md](recon/cve_lookup.md) |

### 网页

| 工具 | 用途 | 页面 |
|---|---|---|
| `nikto_scan` | 扫描网页服务器的常见发现项和错误配置。 | [web/nikto_scan.md](web/nikto_scan.md) |
| `gobuster_dir` | 使用字典发现网页目录和文件。 | [web/gobuster_dir.md](web/gobuster_dir.md) |
| `dirb_scan` | 使用 DIRB 发现网页内容。 | [web/dirb_scan.md](web/dirb_scan.md) |
| `wfuzz_scan` | 对路径、参数、虚拟主机和其他网页输入进行模糊测试。 | [web/wfuzz_scan.md](web/wfuzz_scan.md) |
| `ffuf_fuzz` | 快速模糊测试目录、参数和虚拟主机。 | [web/ffuf_fuzz.md](web/ffuf_fuzz.md) |
| `nuclei_scan` | 使用模板检查漏洞、暴露面和错误配置。 | [web/nuclei_scan.md](web/nuclei_scan.md) |
| `wpscan` | 扫描 WordPress 核心、插件、主题和用户。 | [web/wpscan.md](web/wpscan.md) |
| `joomscan` | 扫描 Joomla 组件和已知发现项。 | [web/joomscan.md](web/joomscan.md) |
| `zap_scan` | 运行 OWASP ZAP 的爬取、被动、主动或完整网页扫描。 | [web/zap_scan.md](web/zap_scan.md) |

### 利用

| 工具 | 用途 | 页面 |
|---|---|---|
| `sqlmap_scan` | 使用 sqlmap 检测和验证 SQL 注入。 | [exploitation/sqlmap_scan.md](exploitation/sqlmap_scan.md) |
| `msf_console` | 运行 Metasploit 控制台命令或资源脚本。 | [exploitation/msf_console.md](exploitation/msf_console.md) |
| `msfvenom` | 使用 msfvenom 生成 Metasploit 载荷。 | [exploitation/msfvenom.md](exploitation/msfvenom.md) |
| `metasploit_resource` | 创建或运行 Metasploit 资源脚本。 | [exploitation/metasploit_resource.md](exploitation/metasploit_resource.md) |

### 凭据

| 工具 | 用途 | 页面 |
|---|---|---|
| `hydra_attack` | 使用 Hydra 做在线口令猜测或密码喷洒。 | [credentials/hydra_attack.md](credentials/hydra_attack.md) |
| `medusa_bruteforce` | 使用 Medusa 做并行在线口令猜测。 | [credentials/medusa_bruteforce.md](credentials/medusa_bruteforce.md) |
| `ncrack_bruteforce` | 使用 Ncrack 做高速网络认证破解。 | [credentials/ncrack_bruteforce.md](credentials/ncrack_bruteforce.md) |
| `hashcat_crack` | 使用 Hashcat 离线破解密码哈希。 | [credentials/hashcat_crack.md](credentials/hashcat_crack.md) |
| `john_crack` | 使用 John the Ripper 离线破解密码哈希并识别格式。 | [credentials/john_crack.md](credentials/john_crack.md) |

### 文件共享与活动目录

| 工具 | 用途 | 页面 |
|---|---|---|
| `enum4linux_scan` | 枚举文件共享和网络基本输入输出系统中的用户、共享、组和策略。 | [smb-ad/enum4linux_scan.md](smb-ad/enum4linux_scan.md) |
| `crackmapexec` | 在 Windows 或活动目录网络中验证凭据、枚举并运行模块。 | [smb-ad/crackmapexec.md](smb-ad/crackmapexec.md) |
| `impacket_scripts` | 运行 Impacket 脚本完成 Windows 或活动目录认证、枚举和执行。 | [smb-ad/impacket_scripts.md](smb-ad/impacket_scripts.md) |
| `bloodhound_enum` | 采集活动目录关系数据，供 BloodHound 分析。 | [smb-ad/bloodhound_enum.md](smb-ad/bloodhound_enum.md) |

### 网络与中间人

| 工具 | 用途 | 页面 |
|---|---|---|
| `netcat_connect` | 建立 TCP 连接、监听器和轻量横幅检查。 | [network-mitm/netcat_connect.md](network-mitm/netcat_connect.md) |
| `tcpdump_capture` | 以文本或数据包文件形式捕获网络流量。 | [network-mitm/tcpdump_capture.md](network-mitm/tcpdump_capture.md) |
| `bettercap_scan` | 运行 BetterCAP 网络发现、嗅探和中间人流程。 | [network-mitm/bettercap_scan.md](network-mitm/bettercap_scan.md) |
| `responder_poison` | 运行 Responder 分析或名称解析投毒。 | [network-mitm/responder_poison.md](network-mitm/responder_poison.md) |
| `ettercap_mitm` | 运行 Ettercap 中间人攻击和插件。 | [network-mitm/ettercap_mitm.md](network-mitm/ettercap_mitm.md) |

### 无线

| 工具 | 用途 | 页面 |
|---|---|---|
| `aircrack_suite` | 运行 Aircrack-ng 的监听、抓包、注入和破解流程。 | [wireless/aircrack_suite.md](wireless/aircrack_suite.md) |
| `wifite_audit` | 使用 Wifite 做自动化无线审计。 | [wireless/wifite_audit.md](wireless/wifite_audit.md) |

### 社会工程与指挥控制

| 工具 | 用途 | 页面 |
|---|---|---|
| `setoolkit` | 运行 Social Engineering Toolkit 工作流。 | [social-c2/setoolkit.md](social-c2/setoolkit.md) |
| `beef_start` | 启动或控制 BeEF 浏览器利用框架。 | [social-c2/beef_start.md](social-c2/beef_start.md) |

### 实用工具

| 工具 | 用途 | 页面 |
|---|---|---|
| `shell_command` | 通过 MCP 服务端运行简单 shell 命令。 | [utilities/shell_command.md](utilities/shell_command.md) |
| `get_scan_history` | 查询保存在 SQLite 中的扫描历史。 | [utilities/get_scan_history.md](utilities/get_scan_history.md) |
| `generate_report` | 从扫描历史生成 Markdown 报告。 | [utilities/generate_report.md](utilities/generate_report.md) |
| `crunch_gen` | 按长度、字符集或模式生成字典。 | [utilities/crunch_gen.md](utilities/crunch_gen.md) |
| `cewl_gen` | 从目标网站内容生成定制字典。 | [utilities/cewl_gen.md](utilities/cewl_gen.md) |
