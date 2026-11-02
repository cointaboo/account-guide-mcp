#!/usr/bin/env python3
"""账号指南 MCP Server（无依赖，stdio JSON-RPC）

给 Claude Desktop / Cursor / Codex 用的只读知识库：
  search_guides  关键词检索 154 篇中文实操指南
  get_guide      取某一篇全文
  list_guides    列出全部标题

数据来自 yuantou.one/guide，本地构建成 JSON 索引后离线可查。
"""
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(BASE, "guides.json")
SITE = "https://yuantou.one/guide/"

_data = None


def data():
    global _data
    if _data is None:
        with open(INDEX, encoding="utf-8") as f:
            _data = json.load(f)
    return _data


def search(q, limit=5):
    q = (q or "").strip().lower()
    if not q:
        return []
    words = [w for w in re.split(r"\s+", q) if w]
    scored = []
    for g in data():
        t = g["title"].lower()
        b = g["body"].lower()
        s = 0
        for w in words:
            if w in t:
                s += 10
            s += min(b.count(w), 5)
        if s:
            scored.append((s, g))
    scored.sort(key=lambda x: -x[0])
    out = []
    for s, g in scored[:limit]:
        snippet = g["body"][:180].replace("\n", " ")
        out.append({"title": g["title"], "url": SITE + g["slug"] + ".html",
                    "snippet": snippet, "score": s})
    return out


TOOLS = [
    {
        "name": "search_guides",
        "description": "检索中文账号实操指南（Apple ID、Telegram、X、AI 订阅、支付、风控与解封）。返回标题、原文链接和摘要。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "关键词，如 apple id 被禁用 / telegram 无法发言"},
                "limit": {"type": "integer", "description": "返回条数，默认 5"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_guide",
        "description": "按 slug 取一篇指南全文（slug 可从 search_guides 的 url 里得到）。",
        "inputSchema": {
            "type": "object",
            "properties": {"slug": {"type": "string"}},
            "required": ["slug"],
        },
    },
    {
        "name": "list_guides",
        "description": "列出全部指南标题与链接。",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def call(name, args):
    if name == "search_guides":
        return search(args.get("query", ""), int(args.get("limit") or 5))
    if name == "get_guide":
        slug = (args.get("slug") or "").strip()
        for g in data():
            if g["slug"] == slug:
                return {"title": g["title"], "url": SITE + slug + ".html", "body": g["body"]}
        return {"error": "not found"}
    if name == "list_guides":
        return [{"title": g["title"], "url": SITE + g["slug"] + ".html"} for g in data()]
    raise ValueError("unknown tool: " + name)


def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        mid = req.get("id")
        method = req.get("method")
        params = req.get("params") or {}

        if method == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "account-guide", "version": "1.0.0"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            try:
                res = call(params.get("name"), params.get("arguments") or {})
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text", "text": json.dumps(res, ensure_ascii=False, indent=1)}]}})
            except Exception as e:
                send({"jsonrpc": "2.0", "id": mid, "isError": True,
                      "result": {"content": [{"type": "text", "text": str(e)}]}})
        elif method in ("notifications/initialized", "initialized"):
            continue
        elif mid is not None:
            send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}})


if __name__ == "__main__":
    main()
