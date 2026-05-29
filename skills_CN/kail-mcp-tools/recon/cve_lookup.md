# `cve_lookup`

- 用途：按编号、关键词、通用平台枚举、严重度或日期查询 NVD 漏洞数据。

## 参数
- `cve_id`（字符串）：精确漏洞编号。
- `keyword`（字符串）：关键词搜索字符串。
- `exact_match`（布尔值，默认值=false）：要求关键词精确匹配。
- `cpe_name`（字符串）：通用平台枚举名称过滤器。
- `virtual_match_string`（字符串）：通用平台枚举匹配字符串过滤器。
- `cvss_severity`（字符串）：通用漏洞评分系统第三版严重度过滤器。 可选值：`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`。
- `pub_start_date`（字符串）：发布日期起点，格式为 YYYY-MM-DD。
- `pub_end_date`（字符串）：发布日期终点，格式为 YYYY-MM-DD。
- `last_mod_start_date`（字符串）：最后修改日期起点，格式为 YYYY-MM-DD。
- `last_mod_end_date`（字符串）：最后修改日期终点，格式为 YYYY-MM-DD。
- `no_rejected`（布尔值，默认值=false）：排除已拒绝的漏洞记录。
- `max_results`（整数，默认值=5）：最大结果数量。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "cve_lookup",
  "arguments": {
    "keyword": "OpenSSH 7.9",
    "cvss_severity": "HIGH",
    "no_rejected": true,
    "max_results": 5
  }
}
```

## 使用要点
- 优先使用产品名加版本号，或精确的通用平台枚举，以减少误匹配。

## 相关知识
- [knowledge/tools/cve_lookup.md](../../../knowledge/tools/cve_lookup.md)
