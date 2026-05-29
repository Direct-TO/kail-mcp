# `tcpdump_capture`

- 用途：以文本或数据包文件形式捕获网络流量。

## 参数
- `interface`（字符串，必填，默认值="eth0"）：网络接口。
- `filter`（字符串）：数据包过滤表达式。
- `count`（整数，默认值=100）：数据包数量。
- `output_file`（字符串）：输出文件路径。
- `verbose`（布尔值，默认值=false）：详细输出。
- `duration`（整数）：捕获持续时间，单位为秒。

## 示例
通过 MCP `tools/call` 调用：

```json
{
  "name": "tcpdump_capture",
  "arguments": {
    "interface": "eth0",
    "filter": "host 192.168.56.10",
    "count": 100,
    "output_file": "/tmp/capture.pcap"
  }
}
```

## 使用要点
- 使用 filter、count 或 duration 缩小抓包内容。

## 相关知识
- [knowledge/tools/netcat.md](../../../knowledge/tools/netcat.md)
