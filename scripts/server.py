#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
server.py
启动本地股票研究估值看板 HTTP 服务。
网页打开后，点击页面上的【🔄 同步数据】按钮可直接通过 HTTP 接口触发数据同步脚本，自动重构并即时刷新看板。
"""

import os
import sys

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPTS_DIR)

from sync_overview import sync_all, start_server

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print("正在预先同步最新估值数据...")
    sync_all()
    start_server(port)
