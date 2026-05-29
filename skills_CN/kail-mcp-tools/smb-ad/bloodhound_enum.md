# `bloodhound_enum`

- 用途：采集活动目录关系数据，供 BloodHound 分析。

## 参数
- `target`（字符串，必填）：目标主机、IP、范围或域名，具体含义取决于工具。
- `username`（字符串，必填）：用户名或用户名文件。
- `password`（字符串，必填）：密码或密码文件。
- `domain`（字符串，必填）：域名。
- `collector`（字符串，默认值="BloodHound.py"）：采集器实现。 可选值：`BloodHound.py`。
- `collection_methods`（字符串数组）：采集方法。
- `zip_filename`（字符串）：输出压缩包文件名。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "bloodhound_enum",
  "arguments": {
    "target": "dc01.example.test",
    "username": "audit",
    "password": "<known-password>",
    "domain": "example.test",
    "collection_methods": [
      "Group",
      "LocalAdmin"
    ]
  }
}
```

## 使用要点
- 需要有效域凭据；输出用于 BloodHound 关系分析。

## 相关知识
- [knowledge/tools/ad_tools.md](../../../knowledge/tools/ad_tools.md)
