#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py
Market Monitor 实时行情与估值偏差看板独立本地服务。
提供 /api/quotes 接口供看板交互式轮询最新行情，并提供静态资源托管。
"""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

# 兼容 Windows GBK 控制台编码输出
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, MODULE_DIR)

from monitor import get_market_snapshot, load_exclusions, save_exclusions

WORKSPACE_DIR = os.path.abspath(os.path.join(MODULE_DIR, ".."))

class MonitorRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 静态文件从 stock-research 根目录服务，方便访问相对路径文件
        super().__init__(*args, directory=WORKSPACE_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/exclusions"):
            self.handle_get_exclusions()
        elif self.path.startswith("/api/quotes"):
            self.handle_quotes()
        elif self.path in ["/", "/index.html", "/market-monitor", "/market-monitor/"]:
            self.send_response(302)
            self.send_header("Location", "/market-monitor/market-dashboard.html")
            self.end_headers()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/exclusions"):
            self.handle_post_exclusions()
        elif self.path in ["/api/quotes", "/api/refresh"]:
            self.handle_quotes()
        else:
            self.send_error(404, "Endpoint Not Found")

    def handle_get_exclusions(self):
        try:
            ex_codes = load_exclusions()
            ex_path = os.path.join(MODULE_DIR, "excluded_stocks.json")
            data = {"excluded_codes": ex_codes, "items": []}
            if os.path.exists(ex_path):
                with open(ex_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

    def handle_post_exclusions(self):
        try:
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
            payload = json.loads(post_body.decode("utf-8"))

            action = payload.get("action", "set")
            target_codes = payload.get("codes", [])
            current_ex = load_exclusions()

            if action == "exclude":
                for c in target_codes:
                    if c not in current_ex:
                        current_ex.append(c)
            elif action == "restore":
                for c in target_codes:
                    if c in current_ex:
                        current_ex.remove(c)
            elif action == "clear":
                current_ex = []
            elif action == "set":
                current_ex = list(target_codes)

            reason_map = payload.get("reasons", {})
            saved_data = save_exclusions(current_ex, reason_map)

            # 同时更新快照
            get_market_snapshot()

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(saved_data, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))

    def handle_quotes(self):
        try:
            snapshot = get_market_snapshot()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(snapshot, ensure_ascii=False).encode("utf-8"))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            err = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(err, ensure_ascii=False).encode("utf-8"))


def start_monitor_server(port=8090):
    server_address = ("", port)
    for p in range(port, port + 10):
        try:
            httpd = HTTPServer(("", p), MonitorRequestHandler)
            port = p
            break
        except OSError:
            continue

    url = f"http://localhost:{port}/market-monitor/market-dashboard.html"
    print("=" * 70)
    print("📊 Market Monitor 收盘行情与估值偏差看板服务已启动！")
    print(f"🔗 看板访问地址: {url}")
    print(f"📡 数据接口 API: http://localhost:{port}/api/quotes")
    print("=" * 70)
    print("提示：看板已载入各标的收盘价与基准偏差数据，支持按需核验，按 Ctrl+C 停止服务。")

    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    start_monitor_server(p)
