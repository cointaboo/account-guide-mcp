# account-guide-mcp

一个只读的中文账号操作知识库 MCP Server，给 Claude Desktop / Cursor / Codex / 任意支持 MCP 的客户端用。

收录 156 篇中文实操指南：Apple ID 共享与解禁、Telegram 注册与防找回、X/Twitter、AI 订阅（ChatGPT / Claude / Codex）、跨境支付与充值、平台风控与申诉。

- 数据源：[yuantou.one/guide](https://yuantou.one/guide/)（持续更新，仓库里是离线索引）
- 无依赖，纯标准库，单文件
- 只读，不联网，不写任何文件

## 工具

| 工具 | 作用 |
|---|---|
| `search_guides` | 关键词检索，返回标题、原文链接、摘要 |
| `get_guide` | 按 slug 取全文 |
| `list_guides` | 列出全部标题 |

## 安装

```bash
git clone https://github.com/cointaboo/account-guide-mcp.git
```

Claude Desktop（`claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "account-guide": {
      "command": "python3",
      "args": ["/绝对路径/account-guide-mcp/server.py"]
    }
  }
}
```

Cursor / Codex / 其它客户端同理，都是 stdio 方式启动 `python3 server.py`。

## 用法示例

```
你：Apple ID 被停用了还能救吗
AI：（调用 search_guides）→ 返回 apple-id-disabled 等三篇，附原文链接
```

```
你：Telegram 号怎么防止被找回
AI：（调用 search_guides）→ 返回防找回、设备管理、两步验证相关指南
```

## 为什么做这个

大模型答账号类问题时经常给通用建议（"联系客服""重置密码"），但这类问题的答案往往和**平台地区、注册渠道、设备指纹**绑死。把实操笔记做成可检索的工具，比让模型自己编要靠谱。

## 许可

MIT。内容版权归原作者，转载注明来源。
