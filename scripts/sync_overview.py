#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_overview.py
股票研究估值总览数据同步脚本。
自动解析 stock-overview.md 与 PROJECT_CONTEXT.md，重新构建并更新 stock-overview.html。
支持独立运行或通过 --serve 启动本地 HTTP 服务以供网页端一键触发。
"""

import os
import re
import json
import sys
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime

# 兼容 Windows 默认 GBK 控制台编码
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.abspath(os.path.join(SCRIPTS_DIR, ".."))
OVERVIEW_MD = os.path.join(WORKSPACE_DIR, "stock-overview.md")
CONTEXT_MD = os.path.join(WORKSPACE_DIR, "PROJECT_CONTEXT.md")
OUTPUT_HTML = os.path.join(WORKSPACE_DIR, "stock-overview.html")

def parse_overview_markdown():
    if not os.path.exists(OVERVIEW_MD):
        raise FileNotFoundError(f"找不到 {OVERVIEW_MD}")

    with open(OVERVIEW_MD, "r", encoding="utf-8") as f:
        content = f.read()

    # 提取最后更新时间
    update_date_match = re.search(r"\*\*最近更新：\*\*\s*([^\n\r]+)", content)
    last_updated = update_date_match.group(1).strip() if update_date_match else datetime.now().strftime("%Y-%m-%d")

    # 提取覆盖公司数
    coverage_match = re.search(r"\*\*覆盖公司：\*\*\s*([^\n\r]+)", content)
    coverage_str = coverage_match.group(1).strip() if coverage_match else "23 家"

    # 提取表格行
    lines = [l.strip() for l in content.splitlines() if l.strip().startswith("|") and not l.strip().startswith("|---")]
    if not lines:
        raise ValueError("未在 stock-overview.md 中找到有效 Markdown 表格")

    data_lines = lines[1:]

    # 解析已完成的主要工作（核心争议与摘要）
    theses = {}
    if os.path.exists(CONTEXT_MD):
        with open(CONTEXT_MD, "r", encoding="utf-8") as f:
            ctx_content = f.read()
        work_sec_m = re.search(r"## 已完成的主要工作(.*?)(?=## 本次会话|## 维护本文件|## 新会话|$)", ctx_content, re.S)
        if work_sec_m:
            for k, v in re.findall(r"-\s*([^：:\n]+)[：:]([^\n]+)", work_sec_m.group(1)):
                theses[k.strip()] = v.strip()

    companies_data = []

    for line in data_lines:
        parts = [p.strip() for p in line.split("|")[1:-1]]
        if len(parts) < 11:
            continue

        comp_name = parts[0]
        ticker = parts[1]
        price_raw = parts[2]
        bear_raw = parts[3]
        base_raw = parts[4]
        bull_raw = parts[5]
        upside_raw = parts[6]
        stance = parts[7]
        method = parts[8]
        cutoff_date = parts[9]
        report_raw = parts[10]

        # 价格与币种
        p_match = re.search(r"([\d\.]+)\s*(港元|元)", price_raw)
        price_val = float(p_match.group(1)) if p_match else 0.0
        currency = p_match.group(2) if p_match else "元"

        # 价格日期
        d_match = re.search(r"(\d{4}-\d{2}-\d{2})", price_raw)
        price_date = d_match.group(1) if d_match else ""

        # 附加说明（盘中、停牌前等）
        extra_note = ""
        if "停牌前" in price_raw:
            extra_note = "停牌前"
        elif "盘中" in price_raw:
            extra_note = "盘中"

        # Bear, Base, Bull
        bear_val = float(re.search(r"([\d\.]+)", bear_raw).group(1))
        base_val = float(re.search(r"([\d\.]+)", base_raw).group(1))
        bull_val = float(re.search(r"([\d\.]+)", bull_raw).group(1))

        # 基准空间数值
        u_match = re.search(r"([+-]?[\d\.]+)%", upside_raw)
        upside_val = float(u_match.group(1)) if u_match else 0.0

        # 研报链接与公司目录
        link_m = re.search(r"\((.*?)\)", report_raw)
        report_link = link_m.group(1) if link_m else ""
        comp_dir = "/".join(report_link.split("/")[:-1])

        # 市场分类
        if ".SH" in ticker and ".HK" in ticker:
            market = "A+H"
        elif ".SZ" in ticker and ".HK" in ticker:
            market = "A+H"
        elif ".HK" in ticker:
            market = "港股"
        else:
            market = "A股"

        # 评级分类归一化
        if "积极" in stance or "吸引力" in stance:
            if "偏积极" in stance:
                stance_type = "neutral_pos"
            else:
                stance_type = "positive"
        elif "偏谨慎" in stance:
            stance_type = "cautious"
        elif "回避" in stance:
            stance_type = "avoid"
        else:
            stance_type = "neutral"

        # 匹配核心争议
        thesis_text = ""
        for tk, tv in theses.items():
            if tk in comp_name or comp_name in tk:
                thesis_text = tv
                break

        # 检查目录下实际存在的文件
        full_comp_dir = os.path.join(WORKSPACE_DIR, comp_dir.replace("/", os.sep))
        has_profile = os.path.exists(os.path.join(full_comp_dir, "company-profile.md"))
        has_model = os.path.exists(os.path.join(full_comp_dir, "financial-model.xlsx"))
        has_sources = os.path.exists(os.path.join(full_comp_dir, "source-index.md"))
        has_logs = os.path.exists(os.path.join(full_comp_dir, "update-log.md"))

        companies_data.append({
            "company": comp_name,
            "code": ticker,
            "market": market,
            "price_val": price_val,
            "currency": currency,
            "price_date": price_date,
            "price_extra": extra_note,
            "price_raw": price_raw,
            "bear_val": bear_val,
            "bear_raw": bear_raw,
            "base_val": base_val,
            "base_raw": base_raw,
            "bull_val": bull_val,
            "bull_raw": bull_raw,
            "upside_val": upside_val,
            "upside_str": upside_raw,
            "stance": stance,
            "stance_type": stance_type,
            "method": method,
            "cutoff_date": cutoff_date,
            "report_link": report_link,
            "comp_dir": comp_dir,
            "thesis": thesis_text,
            "has_profile": has_profile,
            "has_model": has_model,
            "has_sources": has_sources,
            "has_logs": has_logs
        })

    # 计算全局 KPI 统计
    total_count = len(companies_data)
    a_count = sum(1 for c in companies_data if "A" in c["market"])
    hk_count = sum(1 for c in companies_data if "港" in c["market"])
    avg_upside = sum(c["upside_val"] for c in companies_data) / total_count if total_count else 0
    sorted_upsides = sorted(c["upside_val"] for c in companies_data)
    median_upside = sorted_upsides[total_count // 2] if total_count else 0
    high_upside_count = sum(1 for c in companies_data if c["upside_val"] > 20)
    max_upside_item = max(companies_data, key=lambda c: c["upside_val"]) if companies_data else None
    downside_count = sum(1 for c in companies_data if c["upside_val"] < 0)
    min_upside_item = min(companies_data, key=lambda c: c["upside_val"]) if companies_data else None
    positive_ratings_count = sum(1 for c in companies_data if c["stance_type"] in ["positive", "neutral_pos"])

    kpis = {
        "total_count": total_count,
        "a_count": a_count,
        "hk_count": hk_count,
        "avg_upside_str": f"{'+' if avg_upside > 0 else ''}{avg_upside:.1f}%",
        "median_upside_str": f"{'+' if median_upside > 0 else ''}{median_upside:.1f}%",
        "high_upside_count": high_upside_count,
        "max_upside_text": f"最高 {max_upside_item['upside_str']}（{max_upside_item['company']}）" if max_upside_item else "",
        "downside_count": downside_count,
        "min_upside_text": f"最低 {min_upside_item['upside_str']}（{min_upside_item['company']}）" if min_upside_item else "",
        "positive_ratings_count": positive_ratings_count,
    }

    return {
        "last_updated": last_updated,
        "coverage_str": coverage_str,
        "kpis": kpis,
        "companies": companies_data
    }


def build_html_content(dataset):
    json_str = json.dumps(dataset, ensure_ascii=False, indent=2)
    k = dataset["kpis"]

    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>股票研究估值总览 · 交互式看板</title>
  <style>
    :root {{
      --bg-main: #0b0f19;
      --bg-surface: #111827;
      --bg-card: #182234;
      --bg-card-hover: #1f2d44;
      --border-color: #273549;
      --border-subtle: #1e293b;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent: #38bdf8;
      --accent-rgb: 56, 189, 248;
      --positive: #10b981;
      --positive-bg: rgba(16, 185, 129, 0.12);
      --positive-border: rgba(16, 185, 129, 0.3);
      --negative: #f43f5e;
      --negative-bg: rgba(244, 63, 94, 0.12);
      --negative-border: rgba(244, 63, 94, 0.3);
      --neutral: #64748b;
      --neutral-bg: rgba(100, 116, 139, 0.12);
      --neutral-border: rgba(100, 116, 139, 0.3);
      --cautious: #f59e0b;
      --cautious-bg: rgba(245, 158, 11, 0.12);
      --cautious-border: rgba(245, 158, 11, 0.3);
      --pos-teal: #14b8a6;
      --pos-teal-bg: rgba(20, 184, 166, 0.12);
      --pos-teal-border: rgba(20, 184, 166, 0.3);
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.4);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -4px rgba(0, 0, 0, 0.5);
    }}

    html.light {{
      --bg-main: #f1f5f9;
      --bg-surface: #ffffff;
      --bg-card: #ffffff;
      --bg-card-hover: #f8fafc;
      --border-color: #cbd5e1;
      --border-subtle: #e2e8f0;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-dim: #94a3b8;
      --accent: #0284c7;
      --accent-rgb: 2, 132, 199;
      --positive: #059669;
      --positive-bg: #ecfdf5;
      --positive-border: #a7f3d0;
      --negative: #e11d48;
      --negative-bg: #fff1f2;
      --negative-border: #fecdd3;
      --neutral: #475569;
      --neutral-bg: #f1f5f9;
      --neutral-border: #cbd5e1;
      --cautious: #d97706;
      --cautious-bg: #fffbeb;
      --cautious-border: #fde68a;
      --pos-teal: #0d9488;
      --pos-teal-bg: #f0fdfa;
      --pos-teal-border: #99f6e4;
      --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
      --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.06);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background-color: var(--bg-main);
      color: var(--text-main);
      line-height: 1.5;
      padding: 24px;
      min-height: 100vh;
      transition: background-color 0.2s ease, color 0.2s ease;
    }}

    .mono {{
      font-family: ui-monospace, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    }}

    .container {{
      max-width: 1680px;
      margin: 0 auto;
    }}

    /* Header */
    .header {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      margin-bottom: 24px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border-color);
    }}

    .header-title-wrap h1 {{
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.02em;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .header-title-wrap p {{
      color: var(--text-muted);
      font-size: 14px;
      margin-top: 4px;
    }}

    .badge-date {{
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      color: var(--accent);
      padding: 3px 10px;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 600;
    }}

    .header-actions {{
      display: flex;
      gap: 10px;
      align-items: center;
      flex-wrap: wrap;
    }}

    .btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      border: 1px solid var(--border-color);
      background: var(--bg-card);
      color: var(--text-main);
      transition: all 0.15s ease;
      text-decoration: none;
    }}

    .btn:hover {{
      background: var(--bg-card-hover);
      border-color: var(--accent);
      color: var(--accent);
    }}

    .btn-sync {{
      background: rgba(16, 185, 129, 0.15);
      color: var(--positive);
      border-color: var(--positive-border);
      font-weight: 600;
    }}

    .btn-sync:hover {{
      background: var(--positive);
      color: #ffffff;
      border-color: var(--positive);
    }}

    .btn-sync.syncing {{
      pointer-events: none;
      opacity: 0.7;
    }}

    .btn-primary {{
      background: var(--accent);
      color: #0b0f19;
      border-color: var(--accent);
      font-weight: 600;
    }}

    html.light .btn-primary {{
      color: #ffffff;
    }}

    .btn-primary:hover {{
      opacity: 0.9;
      background: var(--accent);
      color: #0b0f19;
    }}

    html.light .btn-primary:hover {{
      color: #ffffff;
    }}

    /* KPI Summary Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 16px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .kpi-card:hover {{
      border-color: var(--border-color);
      transform: translateY(-2px);
    }}

    .kpi-label {{
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .kpi-value {{
      font-size: 26px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .kpi-subtext {{
      font-size: 12px;
      color: var(--text-dim);
      margin-top: 4px;
    }}

    /* Filter & Controls Toolbar */
    .toolbar {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 20px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      gap: 14px;
    }}

    .toolbar-row {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }}

    .search-box {{
      position: relative;
      flex: 1;
      min-width: 260px;
      max-width: 440px;
    }}

    .search-input {{
      width: 100%;
      background: var(--bg-main);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 9px 12px 9px 36px;
      font-size: 13px;
      color: var(--text-main);
      outline: none;
      transition: border-color 0.15s ease;
    }}

    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 0 2px rgba(var(--accent-rgb), 0.2);
    }}

    .search-icon {{
      position: absolute;
      left: 11px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-dim);
      pointer-events: none;
    }}

    .pill-group {{
      display: inline-flex;
      background: var(--bg-main);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 3px;
      gap: 2px;
    }}

    .pill-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      padding: 5px 12px;
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
    }}

    .pill-btn:hover {{
      color: var(--text-main);
    }}

    .pill-btn.active {{
      background: var(--bg-card);
      color: var(--text-main);
      box-shadow: var(--shadow-sm);
      font-weight: 600;
      border: 1px solid var(--border-color);
    }}

    .view-tabs {{
      display: inline-flex;
      background: var(--bg-main);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 3px;
      gap: 2px;
    }}

    .view-tab-btn {{
      border: none;
      background: transparent;
      color: var(--text-muted);
      padding: 6px 14px;
      border-radius: 6px;
      font-size: 13px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      font-weight: 500;
      transition: all 0.15s ease;
    }}

    .view-tab-btn.active {{
      background: var(--accent);
      color: #0b0f19;
      font-weight: 600;
    }}

    html.light .view-tab-btn.active {{
      color: #ffffff;
    }}

    .active-filter-hint {{
      font-size: 12px;
      color: var(--text-dim);
    }}

    /* Table Styles */
    .table-container {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      overflow-x: auto;
      box-shadow: var(--shadow-sm);
      margin-bottom: 24px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
      text-align: left;
    }}

    thead {{
      background: var(--bg-card);
      border-bottom: 2px solid var(--border-color);
      position: sticky;
      top: 0;
      z-index: 10;
    }}

    th {{
      padding: 12px 14px;
      color: var(--text-muted);
      font-weight: 600;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      white-space: nowrap;
      user-select: none;
      cursor: pointer;
      transition: background-color 0.15s ease, color 0.15s ease;
    }}

    th:hover {{
      background-color: var(--bg-card-hover);
      color: var(--text-main);
    }}

    th .th-content {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    th.sorted-asc, th.sorted-desc {{
      color: var(--accent);
    }}

    th.sorted-asc::after {{
      content: " ▲";
      font-size: 10px;
    }}

    th.sorted-desc::after {{
      content: " ▼";
      font-size: 10px;
    }}

    tbody tr {{
      border-bottom: 1px solid var(--border-subtle);
      cursor: pointer;
      transition: background-color 0.15s ease;
    }}

    tbody tr:hover {{
      background-color: var(--bg-card-hover);
    }}

    tbody tr:last-child {{
      border-bottom: none;
    }}

    td {{
      padding: 12px 14px;
      vertical-align: middle;
      white-space: nowrap;
    }}

    .col-company {{
      font-weight: 600;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .badge-market {{
      font-size: 10px;
      padding: 2px 6px;
      border-radius: 4px;
      font-weight: 600;
    }}

    .badge-market.ah {{
      background: rgba(147, 51, 234, 0.15);
      color: #c084fc;
      border: 1px solid rgba(147, 51, 234, 0.3);
    }}

    .badge-market.a {{
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }}

    .badge-market.hk {{
      background: rgba(245, 158, 11, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(245, 158, 11, 0.3);
    }}

    .badge-stance {{
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 6px;
      font-weight: 600;
      display: inline-block;
    }}

    .stance-positive {{
      background: var(--positive-bg);
      color: var(--positive);
      border: 1px solid var(--positive-border);
    }}

    .stance-neutral_pos {{
      background: var(--pos-teal-bg);
      color: var(--pos-teal);
      border: 1px solid var(--pos-teal-border);
    }}

    .stance-neutral {{
      background: var(--neutral-bg);
      color: var(--neutral);
      border: 1px solid var(--neutral-border);
    }}

    .stance-cautious {{
      background: var(--cautious-bg);
      color: var(--cautious);
      border: 1px solid var(--cautious-border);
    }}

    .stance-avoid {{
      background: var(--negative-bg);
      color: var(--negative);
      border: 1px solid var(--negative-border);
    }}

    .upside-pill {{
      font-weight: 700;
      font-size: 13px;
      display: inline-block;
      min-width: 68px;
      text-align: right;
    }}

    .upside-positive {{
      color: var(--positive);
    }}

    .upside-negative {{
      color: var(--negative);
    }}

    /* Range Bar Mini Visualization inside Table */
    .range-bar-cell {{
      min-width: 140px;
      max-width: 180px;
    }}

    .range-bar-track {{
      height: 6px;
      background: var(--bg-main);
      border-radius: 9999px;
      position: relative;
      margin: 8px 0 4px 0;
      border: 1px solid var(--border-subtle);
    }}

    .range-bar-span {{
      position: absolute;
      top: 0;
      bottom: 0;
      background: rgba(56, 189, 248, 0.25);
      border-radius: 9999px;
    }}

    .range-bar-pin {{
      position: absolute;
      top: -4px;
      width: 3px;
      height: 14px;
      border-radius: 2px;
      transform: translateX(-50%);
    }}

    .pin-price {{
      background: #38bdf8;
      z-index: 3;
      box-shadow: 0 0 4px rgba(56, 189, 248, 0.8);
    }}

    .pin-base {{
      background: #f59e0b;
      z-index: 2;
      width: 2px;
      height: 10px;
      top: -2px;
    }}

    .range-bar-labels {{
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--text-dim);
    }}

    .action-links {{
      display: inline-flex;
      gap: 5px;
    }}

    .action-btn {{
      font-size: 11px;
      padding: 3px 7px;
      border-radius: 5px;
      background: var(--bg-main);
      border: 1px solid var(--border-color);
      color: var(--accent);
      text-decoration: none;
      font-weight: 500;
      transition: all 0.15s ease;
    }}

    .action-btn:hover {{
      background: var(--accent);
      color: #0b0f19;
    }}

    html.light .action-btn:hover {{
      color: #ffffff;
    }}

    /* Ranking Chart View */
    .chart-view {{
      display: none;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 24px;
      margin-bottom: 24px;
      box-shadow: var(--shadow-sm);
    }}

    .chart-view.active {{
      display: block;
    }}

    .chart-row {{
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 12px;
      padding: 6px 10px;
      border-radius: 8px;
      cursor: pointer;
      transition: background-color 0.15s ease;
    }}

    .chart-row:hover {{
      background-color: var(--bg-card-hover);
    }}

    .chart-company-info {{
      width: 170px;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}

    .chart-company-name {{
      font-weight: 600;
      font-size: 13px;
    }}

    .chart-company-code {{
      font-size: 11px;
      color: var(--text-dim);
    }}

    .chart-bar-area {{
      flex: 1;
      height: 28px;
      background: var(--bg-main);
      border-radius: 6px;
      position: relative;
      display: flex;
      align-items: center;
      border: 1px solid var(--border-subtle);
    }}

    .chart-zero-line {{
      position: absolute;
      top: 0;
      bottom: 0;
      width: 1px;
      background: var(--border-color);
      left: 50%;
      z-index: 1;
    }}

    .chart-bar {{
      position: absolute;
      height: 16px;
      border-radius: 4px;
      transition: width 0.3s ease;
      display: flex;
      align-items: center;
      font-size: 11px;
      font-weight: 600;
      color: #ffffff;
    }}

    .chart-bar.positive {{
      background: linear-gradient(90deg, #10b981, #059669);
      left: 50%;
      padding-left: 8px;
    }}

    .chart-bar.negative {{
      background: linear-gradient(90deg, #e11d48, #f43f5e);
      right: 50%;
      justify-content: flex-end;
      padding-right: 8px;
    }}

    .chart-val-label {{
      width: 70px;
      text-align: right;
      font-size: 13px;
      font-weight: 700;
      flex-shrink: 0;
    }}

    /* Card Grid View */
    .card-grid-view {{
      display: none;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .card-grid-view.active {{
      display: grid;
    }}

    .stock-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 12px;
      padding: 18px;
      box-shadow: var(--shadow-sm);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      gap: 12px;
      cursor: pointer;
      transition: transform 0.15s ease, border-color 0.15s ease;
    }}

    .stock-card:hover {{
      transform: translateY(-2px);
      border-color: var(--accent);
    }}

    .stock-card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .stock-card-title {{
      font-size: 16px;
      font-weight: 700;
    }}

    .stock-card-code {{
      font-size: 12px;
      color: var(--text-dim);
    }}

    .stock-card-numbers {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      background: var(--bg-main);
      padding: 10px;
      border-radius: 8px;
      border: 1px solid var(--border-subtle);
    }}

    .stock-card-num-item {{
      display: flex;
      flex-direction: column;
    }}

    .stock-card-num-label {{
      font-size: 11px;
      color: var(--text-dim);
    }}

    .stock-card-num-val {{
      font-size: 14px;
      font-weight: 600;
    }}

    .stock-card-thesis {{
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .stock-card-footer {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-top: 1px solid var(--border-subtle);
      padding-top: 10px;
      margin-top: 4px;
    }}

    /* Detail Drawer / Modal */
    .drawer-overlay {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.6);
      backdrop-filter: blur(4px);
      z-index: 99;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.2s ease;
    }}

    .drawer-overlay.active {{
      opacity: 1;
      pointer-events: auto;
    }}

    .drawer {{
      position: fixed;
      top: 0;
      right: 0;
      bottom: 0;
      width: 100%;
      max-width: 580px;
      background: var(--bg-surface);
      border-left: 1px solid var(--border-color);
      z-index: 100;
      transform: translateX(100%);
      transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
      display: flex;
      flex-direction: column;
      box-shadow: var(--shadow-lg);
    }}

    .drawer.active {{
      transform: translateX(0);
    }}

    .drawer-header {{
      padding: 20px 24px;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
    }}

    .drawer-title {{
      font-size: 20px;
      font-weight: 700;
    }}

    .drawer-subtitle {{
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .drawer-close {{
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 24px;
      cursor: pointer;
      line-height: 1;
      padding: 4px;
      border-radius: 6px;
      transition: color 0.15s ease;
    }}

    .drawer-close:hover {{
      color: var(--text-main);
    }}

    .drawer-body {{
      padding: 24px;
      overflow-y: auto;
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .drawer-section {{
      background: var(--bg-main);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      padding: 16px;
    }}

    .drawer-section-title {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .scenarios-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 10px;
      margin-top: 8px;
    }}

    .scenario-box {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 12px;
      text-align: center;
    }}

    .scenario-name {{
      font-size: 11px;
      color: var(--text-dim);
      font-weight: 600;
    }}

    .scenario-val {{
      font-size: 16px;
      font-weight: 700;
      margin: 4px 0;
    }}

    .scenario-diff {{
      font-size: 11px;
      font-weight: 600;
    }}

    .drawer-doc-links {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}

    .drawer-doc-btn {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 10px 14px;
      color: var(--text-main);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.15s ease;
    }}

    .drawer-doc-btn:hover {{
      border-color: var(--accent);
      color: var(--accent);
      background: var(--bg-card-hover);
    }}

    .drawer-doc-btn.primary {{
      grid-column: span 2;
      background: rgba(var(--accent-rgb), 0.1);
      border-color: rgba(var(--accent-rgb), 0.4);
      color: var(--accent);
      font-weight: 600;
    }}

    /* Sync Modal Dialog */
    .sync-modal {{
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%) scale(0.95);
      background: var(--bg-surface);
      border: 1px solid var(--border-color);
      border-radius: 14px;
      padding: 24px;
      width: 90%;
      max-width: 520px;
      box-shadow: var(--shadow-lg);
      z-index: 101;
      opacity: 0;
      pointer-events: none;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    .sync-modal.active {{
      opacity: 1;
      pointer-events: auto;
      transform: translate(-50%, -50%) scale(1);
    }}

    .sync-modal h3 {{
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .sync-modal p {{
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.6;
      margin-bottom: 14px;
    }}

    .sync-code-box {{
      background: var(--bg-main);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 10px 14px;
      font-size: 12px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .sync-modal-actions {{
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }}

    /* Empty state */
    .empty-state {{
      text-align: center;
      padding: 48px 24px;
      color: var(--text-muted);
    }}

    .empty-state svg {{
      margin-bottom: 12px;
      opacity: 0.5;
    }}

    /* Toast Notification */
    .toast {{
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--bg-card);
      border: 1px solid var(--accent);
      color: var(--text-main);
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 13px;
      box-shadow: var(--shadow-lg);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.25s ease;
      z-index: 1000;
    }}

    .toast.show {{
      transform: translateY(0);
      opacity: 1;
    }}

    /* Responsive */
    @media (max-width: 768px) {{
      body {{
        padding: 12px;
      }}
      .header {{
        flex-direction: column;
        align-items: flex-start;
      }}
      .search-box {{
        max-width: 100%;
      }}
      .drawer {{
        max-width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <header class="header">
      <div class="header-title-wrap">
        <h1>
          股票研究估值总览
          <span class="badge-date">最近更新：{dataset["last_updated"]}</span>
        </h1>
        <p>全库 {dataset["coverage_str"]} 基本面估值快照 · 网页一键触发同步 · 动态多维排序 · 安全边际可视化</p>
      </div>
      <div class="header-actions">
        <!-- 网页端一键同步按钮 -->
        <button class="btn btn-sync" id="syncTriggerBtn" title="从 stock-overview.md 重新同步数据">
          <span id="syncIcon">🔄</span> 同步数据
        </button>
        <button class="btn" id="themeToggleBtn" title="切换深色/浅色模式">
          <span id="themeIcon">☀️</span> 主题
        </button>
        <button class="btn btn-primary" id="exportCsvBtn" title="将当前排序/筛选数据导出为 Excel CSV">
          <span>📥</span> 导出 CSV
        </button>
        <a href="stock-overview.md" class="btn" title="查看原始 Markdown 文件">
          <span>📄</span> Markdown
        </a>
      </div>
    </header>

    <!-- KPI Summary Cards -->
    <section class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">
          <span>覆盖标的总数</span>
          <span>🏢</span>
        </div>
        <div class="kpi-value mono" id="kpiTotal">{k["total_count"]}</div>
        <div class="kpi-subtext" id="kpiMarketSplit">A股 {k["a_count"]} 家 · 港股 {k["hk_count"]} 家</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>全库平均基准空间</span>
          <span>📈</span>
        </div>
        <div class="kpi-value mono" id="kpiAvgUpside" style="color: var(--positive);">{k["avg_upside_str"]}</div>
        <div class="kpi-subtext" id="kpiMedianUpside">中位数 {k["median_upside_str"]} · Base 相对现价</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>高估值空间标的 (>20%)</span>
          <span>🎯</span>
        </div>
        <div class="kpi-value mono" id="kpiHighUpside" style="color: var(--positive);">{k["high_upside_count"]}</div>
        <div class="kpi-subtext" id="kpiHighUpsideText">{k["max_upside_text"]}</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>估值承压/回避标的 (<0%)</span>
          <span>🛡️</span>
        </div>
        <div class="kpi-value mono" id="kpiDownside" style="color: var(--negative);">{k["downside_count"]}</div>
        <div class="kpi-subtext" id="kpiDownsideText">{k["min_upside_text"]}</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">
          <span>积极偏好评级标的</span>
          <span>⭐</span>
        </div>
        <div class="kpi-value mono" id="kpiPositiveCount" style="color: var(--positive);">{k["positive_ratings_count"]}</div>
        <div class="kpi-subtext">谨慎积极 / 吸引力偏高 / 偏积极</div>
      </div>
    </section>

    <!-- Toolbar: Search, Filters & View Toggle -->
    <section class="toolbar">
      <div class="toolbar-row">
        <!-- Search -->
        <div class="search-box">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input type="text" id="searchInput" class="search-input" placeholder="搜索公司、代码、主要方法、争议核心词...">
        </div>

        <!-- View Tabs -->
        <div class="view-tabs">
          <button class="view-tab-btn active" data-view="table">
            <span>📋</span> 表格视图
          </button>
          <button class="view-tab-btn" data-view="chart">
            <span>📊</span> 空间排序图
          </button>
          <button class="view-tab-btn" data-view="card">
            <span>🗂️</span> 卡片视图
          </button>
        </div>
      </div>

      <div class="toolbar-row">
        <!-- Market Filter -->
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span style="font-size: 12px; color: var(--text-dim);">市场:</span>
          <div class="pill-group" id="marketFilters">
            <button class="pill-btn active" data-filter="all">全部</button>
            <button class="pill-btn" data-filter="A股">A股</button>
            <button class="pill-btn" data-filter="港股">港股</button>
          </div>
        </div>

        <!-- Stance Filter -->
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span style="font-size: 12px; color: var(--text-dim);">判断:</span>
          <div class="pill-group" id="stanceFilters">
            <button class="pill-btn active" data-filter="all">全部</button>
            <button class="pill-btn" data-filter="positive">谨慎积极</button>
            <button class="pill-btn" data-filter="neutral_pos">中性偏积极</button>
            <button class="pill-btn" data-filter="neutral">中性观察</button>
            <button class="pill-btn" data-filter="cautious_avoid">偏谨慎/回避</button>
          </div>
        </div>

        <!-- Upside Filter -->
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span style="font-size: 12px; color: var(--text-dim);">空间:</span>
          <div class="pill-group" id="upsideFilters">
            <button class="pill-btn active" data-filter="all">全部</button>
            <button class="pill-btn" data-filter="high">> +20%</button>
            <button class="pill-btn" data-filter="mid">0% ~ 20%</button>
            <button class="pill-btn" data-filter="low">< 0%</button>
          </div>
        </div>

        <!-- Reset Button & Results Count -->
        <div style="display: flex; align-items: center; gap: 12px; margin-left: auto;">
          <span class="active-filter-hint" id="filterCount">显示 {k["total_count"]} / {k["total_count"]} 家</span>
          <button class="btn" id="resetBtn" style="padding: 4px 10px; font-size: 12px;">↺ 重置</button>
        </div>
      </div>
    </section>

    <!-- Table View -->
    <section class="table-container" id="tableView">
      <table id="stocksTable">
        <thead>
          <tr>
            <th data-sort="company"><div class="th-content">公司</div></th>
            <th data-sort="code"><div class="th-content">代码</div></th>
            <th data-sort="price_val" style="text-align: right;"><div class="th-content">价格基准</div></th>
            <th data-sort="bear_val" style="text-align: right;"><div class="th-content">Bear</div></th>
            <th data-sort="base_val" style="text-align: right;"><div class="th-content">Base</div></th>
            <th data-sort="bull_val" style="text-align: right;"><div class="th-content">Bull</div></th>
            <th style="min-width: 150px; text-align: center;"><div class="th-content">估值区间跨度</div></th>
            <th data-sort="upside_val" style="text-align: right;"><div class="th-content">基准空间</div></th>
            <th data-sort="stance_weight"><div class="th-content">当前判断</div></th>
            <th data-sort="method"><div class="th-content">主要方法</div></th>
            <th data-sort="cutoff_date"><div class="th-content">资料截止</div></th>
            <th style="text-align: center;">档案链接</th>
          </tr>
        </thead>
        <tbody id="tableBody">
          <!-- Rows injected by JavaScript -->
        </tbody>
      </table>
    </section>

    <!-- Ranking Chart View -->
    <section class="chart-view" id="chartView">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h3 style="font-size: 16px; font-weight: 600;">基准估值空间对比（Base 相对价格基准，从高到低）</h3>
        <span style="font-size: 12px; color: var(--text-dim);">点击公司条目可展开详细档案</span>
      </div>
      <div id="chartContainer">
        <!-- Bars injected by JavaScript -->
      </div>
    </section>

    <!-- Card Grid View -->
    <section class="card-grid-view" id="cardView">
      <!-- Cards injected by JavaScript -->
    </section>

    <!-- Empty State -->
    <div class="empty-state" id="emptyState" style="display: none;">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <h3>未找到匹配的股票</h3>
      <p style="font-size: 13px; margin-top: 6px;">请尝试更换关键词或清除筛选条件</p>
    </div>
  </div>

  <!-- Detail Slide-Over Drawer -->
  <div class="drawer-overlay" id="drawerOverlay"></div>
  <div class="drawer" id="drawer">
    <div class="drawer-header">
      <div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <div class="drawer-title" id="drawerCompName">公司名称</div>
          <span class="badge-market" id="drawerMarket">A股</span>
          <span class="badge-stance" id="drawerStance">中性观察</span>
        </div>
        <div class="drawer-subtitle mono" id="drawerCode">600000.SH</div>
      </div>
      <button class="drawer-close" id="drawerCloseBtn">&times;</button>
    </div>

    <div class="drawer-body">
      <!-- Key Numbers -->
      <div class="drawer-section">
        <div class="drawer-section-title">
          <span>📊 价格基准与情景估值</span>
        </div>
        <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 12px;">
          <div>
            <span style="font-size: 12px; color: var(--text-dim);">价格基准：</span>
            <span class="mono" style="font-size: 18px; font-weight: 700;" id="drawerPrice">0.00 元</span>
            <span style="font-size: 11px; color: var(--text-dim);" id="drawerPriceDate">（2026-09-08）</span>
          </div>
          <div>
            <span style="font-size: 12px; color: var(--text-dim);">基准空间：</span>
            <span class="mono" style="font-size: 18px; font-weight: 700;" id="drawerUpside">+0.0%</span>
          </div>
        </div>

        <div class="scenarios-grid">
          <div class="scenario-box">
            <div class="scenario-name">悲观 Bear</div>
            <div class="scenario-val mono" id="drawerBear">0.00</div>
            <div class="scenario-diff mono" id="drawerBearDiff">-0.0%</div>
          </div>
          <div class="scenario-box" style="border-color: var(--accent);">
            <div class="scenario-name" style="color: var(--accent);">基准 Base</div>
            <div class="scenario-val mono" id="drawerBase">0.00</div>
            <div class="scenario-diff mono" id="drawerBaseDiff">+0.0%</div>
          </div>
          <div class="scenario-box">
            <div class="scenario-name">乐观 Bull</div>
            <div class="scenario-val mono" id="drawerBull">0.00</div>
            <div class="scenario-diff mono" id="drawerBullDiff">+0.0%</div>
          </div>
        </div>
      </div>

      <!-- Core Thesis & Controversy -->
      <div class="drawer-section">
        <div class="drawer-section-title">
          <span>💡 核心争议与研报摘要</span>
        </div>
        <p style="font-size: 13px; line-height: 1.6; color: var(--text-main);" id="drawerThesis">
          暂无摘要。
        </p>
      </div>

      <!-- Valuation Method -->
      <div class="drawer-section">
        <div class="drawer-section-title">
          <span>📐 主要估值方法与资料截止</span>
        </div>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 8px;">
          <strong style="color: var(--text-main);">主要方法：</strong>
          <span id="drawerMethod">P/E + P/B</span>
        </p>
        <p style="font-size: 13px; color: var(--text-muted);">
          <strong style="color: var(--text-main);">资料截止日期：</strong>
          <span class="mono" id="drawerCutoff">2026-09-08</span>
        </p>
      </div>

      <!-- Quick Action Links -->
      <div class="drawer-section">
        <div class="drawer-section-title">
          <span>📂 关联研究档案与财务模型</span>
        </div>
        <div class="drawer-doc-links">
          <a href="#" class="drawer-doc-btn primary" id="drawerLinkReport" target="_blank">
            <span>📄</span> 查看完整基本面研究报告 (research-report.md)
          </a>
          <a href="#" class="drawer-doc-btn" id="drawerLinkModel">
            <span>📊</span> 财务估值模型 (.xlsx)
          </a>
          <a href="#" class="drawer-doc-btn" id="drawerLinkProfile" target="_blank">
            <span>🏢</span> 公司与治理档案
          </a>
          <a href="#" class="drawer-doc-btn" id="drawerLinkSources" target="_blank">
            <span>📑</span> 数据来源与口径索引
          </a>
          <a href="#" class="drawer-doc-btn" id="drawerLinkLogs" target="_blank">
            <span>📝</span> 历史更新记录
          </a>
        </div>
      </div>
    </div>
  </div>

  <!-- Sync Options Dialog -->
  <div class="sync-modal" id="syncModal">
    <h3><span>🔄</span> 数据同步机制</h3>
    <p>
      数据源为项目根目录的 <code>stock-overview.md</code> 与 <code>PROJECT_CONTEXT.md</code>。
      当您更新了 Markdown 报告或估值数据时，可以通过以下方式同步至本看板：
    </p>

    <div class="sync-code-box">
      <code class="mono" id="cmdText">python scripts/server.py</code>
      <button class="btn" id="copyCmdBtn" style="padding: 4px 8px; font-size: 11px;">复制命令</button>
    </div>

    <p style="font-size: 12px; color: var(--text-dim); margin-bottom: 20px;">
      💡 <strong>启动本地服务后</strong>，点击页面上的“同步数据”按钮即可直接通过 HTTP 触发后台 Python 脚本全自动刷新！<br>
      您也可以直接在终端运行 <code>python scripts/sync_overview.py</code>。
    </p>

    <div class="sync-modal-actions">
      <button class="btn" id="syncFilePickerBtn">📂 选择本地 Markdown 即时解析</button>
      <button class="btn btn-primary" id="closeSyncModalBtn">知道了</button>
    </div>
    <input type="file" id="markdownFileInput" accept=".md" style="display: none;">
  </div>

  <!-- Toast -->
  <div class="toast" id="toast">已成功同步最新数据！</div>

  <!-- Embedded Data & Application Script -->
  <script>
    let DATASET = {json_str};

    const STANCE_ORDER = {{
      '谨慎积极': 1,
      '估值吸引力中等偏高': 2,
      '中性偏积极': 3,
      '中性': 4,
      '中性观察': 5,
      '中性偏谨慎': 6,
      '回避': 7
    }};

    function initDataWeights() {{
      DATASET.companies.forEach(c => {{
        c.stance_weight = STANCE_ORDER[c.stance] || 99;
      }});
    }}
    initDataWeights();

    let currentSort = {{
      key: 'upside_val',
      direction: 'desc'
    }};

    let filters = {{
      search: '',
      market: 'all',
      stance: 'all',
      upside: 'all'
    }};

    let activeView = 'table';

    // DOM Elements
    const tableBody = document.getElementById('tableBody');
    const chartContainer = document.getElementById('chartContainer');
    const cardView = document.getElementById('cardView');
    const searchInput = document.getElementById('searchInput');
    const filterCount = document.getElementById('filterCount');
    const emptyState = document.getElementById('emptyState');
    const toast = document.getElementById('toast');

    // Drawer Elements
    const drawerOverlay = document.getElementById('drawerOverlay');
    const drawer = document.getElementById('drawer');
    const drawerCloseBtn = document.getElementById('drawerCloseBtn');

    // Sync Elements
    const syncTriggerBtn = document.getElementById('syncTriggerBtn');
    const syncIcon = document.getElementById('syncIcon');
    const syncModal = document.getElementById('syncModal');
    const closeSyncModalBtn = document.getElementById('closeSyncModalBtn');
    const copyCmdBtn = document.getElementById('copyCmdBtn');
    const cmdText = document.getElementById('cmdText');
    const syncFilePickerBtn = document.getElementById('syncFilePickerBtn');
    const markdownFileInput = document.getElementById('markdownFileInput');

    // Theme toggle
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');

    function initTheme() {{
      const saved = localStorage.getItem('theme');
      if (saved === 'light' || (!saved && window.matchMedia('(prefers-color-scheme: light)').matches)) {{
        document.documentElement.classList.add('light');
        themeIcon.textContent = '🌙';
      }} else {{
        document.documentElement.classList.remove('light');
        themeIcon.textContent = '☀️';
      }}
    }}

    themeToggleBtn.addEventListener('click', () => {{
      const isLight = document.documentElement.classList.toggle('light');
      localStorage.setItem('theme', isLight ? 'light' : 'dark');
      themeIcon.textContent = isLight ? '🌙' : '☀️';
    }});

    // Helper: Stance class
    function getStanceBadge(stance, stanceType) {{
      return `<span class="badge-stance stance-${{stanceType}}">${{stance}}</span>`;
    }}

    // Helper: Market Badge
    function getMarketBadge(market) {{
      const cls = market === 'A+H' ? 'ah' : (market === '港股' ? 'hk' : 'a');
      return `<span class="badge-market ${{cls}}">${{market}}</span>`;
    }}

    // Helper: Mini Range Bar
    function renderRangeBar(item) {{
      const minVal = Math.min(item.bear_val, item.price_val) * 0.95;
      const maxVal = Math.max(item.bull_val, item.price_val) * 1.05;
      const totalRange = maxVal - minVal || 1;

      const bearLeft = Math.max(0, Math.min(100, ((item.bear_val - minVal) / totalRange) * 100));
      const bullLeft = Math.max(0, Math.min(100, ((item.bull_val - minVal) / totalRange) * 100));
      const baseLeft = Math.max(0, Math.min(100, ((item.base_val - minVal) / totalRange) * 100));
      const priceLeft = Math.max(0, Math.min(100, ((item.price_val - minVal) / totalRange) * 100));

      const spanLeft = Math.min(bearLeft, bullLeft);
      const spanWidth = Math.abs(bullLeft - bearLeft);

      return `
        <div class="range-bar-cell" title="现价: ${{item.price_val}} | Bear: ${{item.bear_val}} | Base: ${{item.base_val}} | Bull: ${{item.bull_val}}">
          <div class="range-bar-track">
            <div class="range-bar-span" style="left: ${{spanLeft}}%; width: ${{spanWidth}}%;"></div>
            <div class="range-bar-pin pin-base" style="left: ${{baseLeft}}%;" title="Base: ${{item.base_val}}"></div>
            <div class="range-bar-pin pin-price" style="left: ${{priceLeft}}%;" title="现价: ${{item.price_val}}"></div>
          </div>
          <div class="range-bar-labels mono">
            <span>${{item.bear_val}}</span>
            <span style="color: var(--accent); font-weight: 600;">现 ${{item.price_val}}</span>
            <span>${{item.bull_val}}</span>
          </div>
        </div>
      `;
    }}

    // Filter Logic
    function getFilteredData() {{
      const query = filters.search.toLowerCase().trim();
      return DATASET.companies.filter(item => {{
        if (query) {{
          const matchComp = item.company.toLowerCase().includes(query);
          const matchCode = item.code.toLowerCase().includes(query);
          const matchMethod = item.method.toLowerCase().includes(query);
          const matchStance = item.stance.toLowerCase().includes(query);
          const matchThesis = (item.thesis || '').toLowerCase().includes(query);
          if (!matchComp && !matchCode && !matchMethod && !matchStance && !matchThesis) {{
            return false;
          }}
        }}

        if (filters.market !== 'all') {{
          if (filters.market === 'A股' && !item.code.includes('.SH') && !item.code.includes('.SZ')) return false;
          if (filters.market === '港股' && !item.code.includes('.HK')) return false;
        }}

        if (filters.stance !== 'all') {{
          if (filters.stance === 'positive' && item.stance_type !== 'positive') return false;
          if (filters.stance === 'neutral_pos' && item.stance_type !== 'neutral_pos') return false;
          if (filters.stance === 'neutral' && item.stance_type !== 'neutral') return false;
          if (filters.stance === 'cautious_avoid' && item.stance_type !== 'cautious' && item.stance_type !== 'avoid') return false;
        }}

        if (filters.upside !== 'all') {{
          if (filters.upside === 'high' && item.upside_val <= 20) return false;
          if (filters.upside === 'mid' && (item.upside_val < 0 || item.upside_val > 20)) return false;
          if (filters.upside === 'low' && item.upside_val >= 0) return false;
        }}

        return true;
      }});
    }}

    // Sort Logic
    function getSortedData(data) {{
      if (!currentSort.key) return data;

      return [...data].sort((a, b) => {{
        let aVal = a[currentSort.key];
        let bVal = b[currentSort.key];

        if (typeof aVal === 'string') {{
          const cmp = aVal.localeCompare(bVal, 'zh-CN');
          return currentSort.direction === 'asc' ? cmp : -cmp;
        }}

        if (aVal < bVal) return currentSort.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return currentSort.direction === 'asc' ? 1 : -1;
        return 0;
      }});
    }}

    // Render Table
    function renderTable(data) {{
      tableBody.innerHTML = '';
      if (data.length === 0) return;

      data.forEach(item => {{
        const tr = document.createElement('tr');
        tr.addEventListener('click', () => openDrawer(item));

        const isPos = item.upside_val >= 0;
        const upsideClass = isPos ? 'upside-positive' : 'upside-negative';

        tr.innerHTML = `
          <td>
            <div class="col-company">
              <span>${{item.company}}</span>
              ${{getMarketBadge(item.market)}}
            </div>
          </td>
          <td><span class="mono" style="color: var(--text-dim);">${{item.code}}</span></td>
          <td style="text-align: right;">
            <div class="mono" style="font-weight: 600;">${{item.price_val.toFixed(2)}} ${{item.currency}}</div>
            <div style="font-size: 11px; color: var(--text-dim);">${{item.price_date}} ${{item.price_extra ? `<span style="color: var(--cautious);">(${{item.price_extra}})</span>` : ''}}</div>
          </td>
          <td style="text-align: right;" class="mono">${{item.bear_val.toFixed(2)}}</td>
          <td style="text-align: right;" class="mono" style="font-weight: 600;">${{item.base_val.toFixed(2)}}</td>
          <td style="text-align: right;" class="mono">${{item.bull_val.toFixed(2)}}</td>
          <td>${{renderRangeBar(item)}}</td>
          <td style="text-align: right;">
            <span class="upside-pill mono ${{upsideClass}}">${{item.upside_str}}</span>
          </td>
          <td>${{getStanceBadge(item.stance, item.stance_type)}}</td>
          <td style="max-width: 220px; overflow: hidden; text-overflow: ellipsis;" title="${{item.method}}">
            <span style="color: var(--text-muted); font-size: 12px;">${{item.method}}</span>
          </td>
          <td class="mono" style="color: var(--text-dim); font-size: 12px;">${{item.cutoff_date}}</td>
          <td style="text-align: center;" onclick="event.stopPropagation();">
            <div class="action-links">
              <a href="${{item.report_link}}" class="action-btn" target="_blank" title="打开研报">研报</a>
              <a href="${{item.comp_dir}}/company-profile.md" class="action-btn" target="_blank" title="公司档案">档案</a>
              <a href="${{item.comp_dir}}/financial-model.xlsx" class="action-btn" title="下载/查看财务模型">模型</a>
            </div>
          </td>
        `;
        tableBody.appendChild(tr);
      }});
    }}

    // Render Ranking Chart
    function renderChart(data) {{
      chartContainer.innerHTML = '';
      if (data.length === 0) return;

      const sorted = [...data].sort((a, b) => b.upside_val - a.upside_val);
      const maxAbs = Math.max(...sorted.map(d => Math.abs(d.upside_val)), 55);

      sorted.forEach(item => {{
        const row = document.createElement('div');
        row.className = 'chart-row';
        row.addEventListener('click', () => openDrawer(item));

        const isPos = item.upside_val >= 0;
        const widthPct = (Math.abs(item.upside_val) / maxAbs) * 50;
        const valClass = isPos ? 'upside-positive' : 'upside-negative';

        row.innerHTML = `
          <div class="chart-company-info">
            <div style="display: flex; align-items: center; gap: 6px;">
              <span class="chart-company-name">${{item.company}}</span>
              ${{getMarketBadge(item.market)}}
            </div>
            <div class="chart-company-code mono">${{item.code}} · ${{item.stance}}</div>
          </div>
          <div class="chart-bar-area">
            <div class="chart-zero-line"></div>
            <div class="chart-bar ${{isPos ? 'positive' : 'negative'}}" style="width: ${{widthPct}}%;">
              ${{isPos && widthPct > 12 ? item.upside_str : ''}}
            </div>
          </div>
          <div class="chart-val-label mono ${{valClass}}">
            ${{item.upside_str}}
          </div>
        `;
        chartContainer.appendChild(row);
      }});
    }}

    // Render Cards
    function renderCards(data) {{
      cardView.innerHTML = '';
      if (data.length === 0) return;

      data.forEach(item => {{
        const card = document.createElement('div');
        card.className = 'stock-card';
        card.addEventListener('click', () => openDrawer(item));

        const isPos = item.upside_val >= 0;
        const upsideClass = isPos ? 'upside-positive' : 'upside-negative';

        card.innerHTML = `
          <div>
            <div class="stock-card-header">
              <div>
                <div class="stock-card-title">${{item.company}}</div>
                <div class="stock-card-code mono">${{item.code}} · ${{item.price_date}}</div>
              </div>
              <div style="text-align: right;">
                <div class="mono upside-pill ${{upsideClass}}" style="font-size: 16px;">${{item.upside_str}}</div>
                ${{getStanceBadge(item.stance, item.stance_type)}}
              </div>
            </div>

            <div class="stock-card-numbers" style="margin-top: 12px;">
              <div class="stock-card-num-item">
                <span class="stock-card-num-label">价格基准</span>
                <span class="stock-card-num-val mono">${{item.price_val.toFixed(2)}} ${{item.currency}}</span>
              </div>
              <div class="stock-card-num-item">
                <span class="stock-card-num-label">基准价值 Base</span>
                <span class="stock-card-num-val mono" style="color: var(--accent);">${{item.base_val.toFixed(2)}}</span>
              </div>
              <div class="stock-card-num-item">
                <span class="stock-card-num-label">悲观 Bear</span>
                <span class="stock-card-num-val mono">${{item.bear_val.toFixed(2)}}</span>
              </div>
              <div class="stock-card-num-item">
                <span class="stock-card-num-label">乐观 Bull</span>
                <span class="stock-card-num-val mono">${{item.bull_val.toFixed(2)}}</span>
              </div>
            </div>

            <div style="margin: 10px 0;">
              ${{renderRangeBar(item)}}
            </div>

            <div class="stock-card-thesis" title="${{item.thesis || item.method}}">
              ${{item.thesis ? `<strong>核心争议：</strong>${{item.thesis}}` : `<strong>方法：</strong>${{item.method}}`}}
            </div>
          </div>

          <div class="stock-card-footer" onclick="event.stopPropagation();">
            <span style="font-size: 11px; color: var(--text-dim);">资料截止: ${{item.cutoff_date}}</span>
            <div class="action-links">
              <a href="${{item.report_link}}" class="action-btn" target="_blank">研报</a>
              <a href="${{item.comp_dir}}/company-profile.md" class="action-btn" target="_blank">档案</a>
              <a href="${{item.comp_dir}}/financial-model.xlsx" class="action-btn">模型</a>
            </div>
          </div>
        `;
        cardView.appendChild(card);
      }});
    }}

    // Master Render
    function render() {{
      const filtered = getFilteredData();
      const sorted = getSortedData(filtered);

      filterCount.textContent = `显示 ${{sorted.length}} / ${{DATASET.companies.length}} 家`;

      if (sorted.length === 0) {{
        emptyState.style.display = 'block';
        tableBody.innerHTML = '';
        chartContainer.innerHTML = '';
        cardView.innerHTML = '';
        return;
      }} else {{
        emptyState.style.display = 'none';
      }}

      if (activeView === 'table') {{
        renderTable(sorted);
      }} else if (activeView === 'chart') {{
        renderChart(sorted);
      }} else if (activeView === 'card') {{
        renderCards(sorted);
      }}

      updateHeaderSortClasses();
    }}

    function updateHeaderSortClasses() {{
      const headers = document.querySelectorAll('th[data-sort]');
      headers.forEach(th => {{
        th.classList.remove('sorted-asc', 'sorted-desc');
        if (th.dataset.sort === currentSort.key) {{
          th.classList.add(currentSort.direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }}
      }});
    }}

    // Table Header Click Sort
    document.querySelectorAll('th[data-sort]').forEach(th => {{
      th.addEventListener('click', () => {{
        const key = th.dataset.sort;
        if (currentSort.key === key) {{
          currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
        }} else {{
          currentSort.key = key;
          currentSort.direction = ['upside_val', 'price_val', 'base_val', 'bull_val', 'bear_val', 'cutoff_date'].includes(key) ? 'desc' : 'asc';
        }}
        render();
      }});
    }});

    // Search Input
    searchInput.addEventListener('input', (e) => {{
      filters.search = e.target.value;
      render();
    }});

    // Pill Filters
    function setupPillGroup(containerId, filterKey) {{
      const container = document.getElementById(containerId);
      container.querySelectorAll('.pill-btn').forEach(btn => {{
        btn.addEventListener('click', () => {{
          container.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          filters[filterKey] = btn.dataset.filter;
          render();
        }});
      }});
    }}

    setupPillGroup('marketFilters', 'market');
    setupPillGroup('stanceFilters', 'stance');
    setupPillGroup('upsideFilters', 'upside');

    // Reset Button
    document.getElementById('resetBtn').addEventListener('click', () => {{
      searchInput.value = '';
      filters.search = '';
      filters.market = 'all';
      filters.stance = 'all';
      filters.upside = 'all';

      document.querySelectorAll('.pill-group').forEach(group => {{
        group.querySelectorAll('.pill-btn').forEach((btn, idx) => {{
          btn.classList.toggle('active', idx === 0);
        }});
      }});

      currentSort = {{ key: 'upside_val', direction: 'desc' }};
      render();
    }});

    // View Switcher
    document.querySelectorAll('.view-tab-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        document.querySelectorAll('.view-tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        activeView = btn.dataset.view;

        document.getElementById('tableView').style.display = activeView === 'table' ? 'block' : 'none';
        document.getElementById('chartView').style.display = activeView === 'chart' ? 'block' : 'none';
        document.getElementById('cardView').style.display = activeView === 'card' ? 'grid' : 'none';

        render();
      }});
    }});

    // Drawer Logic
    function openDrawer(item) {{
      document.getElementById('drawerCompName').textContent = item.company;
      document.getElementById('drawerCode').textContent = item.code;
      document.getElementById('drawerMarket').textContent = item.market;

      const stanceElem = document.getElementById('drawerStance');
      stanceElem.className = `badge-stance stance-${{item.stance_type}}`;
      stanceElem.textContent = item.stance;

      document.getElementById('drawerPrice').textContent = `${{item.price_val.toFixed(2)}} ${{item.currency}}`;
      document.getElementById('drawerPriceDate').textContent = item.price_date ? `（${{item.price_date}}${{item.price_extra ? `，${{item.price_extra}}` : ''}}）` : '';

      const upsideElem = document.getElementById('drawerUpside');
      upsideElem.textContent = item.upside_str;
      upsideElem.className = `mono ${{item.upside_val >= 0 ? 'upside-positive' : 'upside-negative'}}`;

      // Scenarios
      document.getElementById('drawerBear').textContent = `${{item.bear_val.toFixed(2)}} ${{item.currency}}`;
      const bearDiff = item.price_val ? ((item.bear_val - item.price_val) / item.price_val * 100).toFixed(1) : 0;
      const bearDiffElem = document.getElementById('drawerBearDiff');
      bearDiffElem.textContent = `${{bearDiff >= 0 ? '+' : ''}}${{bearDiff}}%`;
      bearDiffElem.className = `scenario-diff mono ${{bearDiff >= 0 ? 'upside-positive' : 'upside-negative'}}`;

      document.getElementById('drawerBase').textContent = `${{item.base_val.toFixed(2)}} ${{item.currency}}`;
      const baseDiffElem = document.getElementById('drawerBaseDiff');
      baseDiffElem.textContent = item.upside_str;
      baseDiffElem.className = `scenario-diff mono ${{item.upside_val >= 0 ? 'upside-positive' : 'upside-negative'}}`;

      document.getElementById('drawerBull').textContent = `${{item.bull_val.toFixed(2)}} ${{item.currency}}`;
      const bullDiff = item.price_val ? ((item.bull_val - item.price_val) / item.price_val * 100).toFixed(1) : 0;
      const bullDiffElem = document.getElementById('drawerBullDiff');
      bullDiffElem.textContent = `${{bullDiff >= 0 ? '+' : ''}}${{bullDiff}}%`;
      bullDiffElem.className = `scenario-diff mono ${{bullDiff >= 0 ? 'upside-positive' : 'upside-negative'}}`;

      // Thesis & Method
      document.getElementById('drawerThesis').textContent = item.thesis || '暂无详细争议，请查阅完整报告。';
      document.getElementById('drawerMethod').textContent = item.method;
      document.getElementById('drawerCutoff').textContent = item.cutoff_date;

      // Action links
      document.getElementById('drawerLinkReport').href = item.report_link;
      document.getElementById('drawerLinkModel').href = `${{item.comp_dir}}/financial-model.xlsx`;
      document.getElementById('drawerLinkProfile').href = `${{item.comp_dir}}/company-profile.md`;
      document.getElementById('drawerLinkSources').href = `${{item.comp_dir}}/source-index.md`;
      document.getElementById('drawerLinkLogs').href = `${{item.comp_dir}}/update-log.md`;

      drawerOverlay.classList.add('active');
      drawer.classList.add('active');
    }}

    function closeDrawer() {{
      drawerOverlay.classList.remove('active');
      drawer.classList.remove('active');
    }}

    drawerCloseBtn.addEventListener('click', closeDrawer);
    drawerOverlay.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Escape') closeDrawer();
    }});

    // Export to CSV
    document.getElementById('exportCsvBtn').addEventListener('click', () => {{
      const sorted = getSortedData(getFilteredData());
      if (sorted.length === 0) return;

      const headers = ['公司', '代码', '市场', '价格基准', '币种', '价格日期', 'Bear(悲观)', 'Base(基准)', 'Bull(乐观)', '基准空间', '当前判断', '主要方法', '资料截止', '报告路径'];

      const csvRows = [headers.join(',')];

      sorted.forEach(d => {{
        const row = [
          `"${{d.company}}"`,
          `"${{d.code}}"`,
          `"${{d.market}}"`,
          d.price_val,
          `"${{d.currency}}"`,
          `"${{d.price_date}}"`,
          d.bear_val,
          d.base_val,
          d.bull_val,
          `"${{d.upside_str}}"`,
          `"${{d.stance}}"`,
          `"${{d.method.replace(/"/g, '""')}}"`,
          `"${{d.cutoff_date}}"`,
          `"${{d.report_link}}"`
        ];
        csvRows.push(row.join(','));
      }});

      const csvContent = "\\uFEFF" + csvRows.join('\\r\\n');
      const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `stock-overview-export-${{new Date().toISOString().slice(0, 10)}}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showToast('已成功导出 CSV 表格！');
    }});

    // ==========================================
    // 网页端数据同步核心逻辑 (Web-triggered Sync)
    // ==========================================
    syncTriggerBtn.addEventListener('click', async () => {{
      syncTriggerBtn.classList.add('syncing');
      syncIcon.textContent = '⏳';

      try {{
        // 尝试向本地服务发起同步 API 请求
        const response = await fetch('/api/sync', {{ method: 'POST' }});
        if (response.ok) {{
          const res = await response.json();
          if (res.status === 'ok' && res.data) {{
            DATASET = res.data;
            initDataWeights();
            updateKPIs(res.data.kpis);
            render();
            showToast(`✅ 同步成功！已刷新 ${{res.data.companies.length}} 家公司最新数据`);
            syncIcon.textContent = '🔄';
            syncTriggerBtn.classList.remove('syncing');
            return;
          }}
        }}
      }} catch (err) {{
        // 若没有运行后台 HTTP 服务（例如以 file:/// 协议直接打开）
        console.log('未检测到本地后台同步服务，尝试本地 Markdown 读取或弹出指引');
      }}

      // 尝试在同源/相对路径下读取 stock-overview.md
      try {{
        const mdRes = await fetch('stock-overview.md?t=' + Date.now());
        if (mdRes.ok) {{
          const mdText = await mdRes.text();
          parseAndApplyMarkdown(mdText);
          showToast('✅ 已从本地 stock-overview.md 成功解析并刷新！');
          syncIcon.textContent = '🔄';
          syncTriggerBtn.classList.remove('syncing');
          return;
        }}
      }} catch (e) {{
        console.log('直接 fetch 本地文件受浏览器安全策略限制');
      }}

      syncIcon.textContent = '🔄';
      syncTriggerBtn.classList.remove('syncing');
      // 弹出同步选项指引弹窗
      openSyncModal();
    }});

    function updateKPIs(k) {{
      if (!k) return;
      document.getElementById('kpiTotal').textContent = k.total_count;
      document.getElementById('kpiMarketSplit').textContent = `A股 ${{k.a_count}} 家 · 港股 ${{k.hk_count}} 家`;
      document.getElementById('kpiAvgUpside').textContent = k.avg_upside_str;
      document.getElementById('kpiMedianUpside').textContent = `中位数 ${{k.median_upside_str}} · Base 相对现价`;
      document.getElementById('kpiHighUpside').textContent = k.high_upside_count;
      document.getElementById('kpiHighUpsideText').textContent = k.max_upside_text;
      document.getElementById('kpiDownside').textContent = k.downside_count;
      document.getElementById('kpiDownsideText').textContent = k.min_upside_text;
      document.getElementById('kpiPositiveCount').textContent = k.positive_ratings_count;
    }}

    function openSyncModal() {{
      syncModal.classList.add('active');
      drawerOverlay.classList.add('active');
    }}

    function closeSyncModal() {{
      syncModal.classList.remove('active');
      if (!drawer.classList.contains('active')) {{
        drawerOverlay.classList.remove('active');
      }}
    }}

    closeSyncModalBtn.addEventListener('click', closeSyncModal);

    copyCmdBtn.addEventListener('click', () => {{
      navigator.clipboard.writeText('python scripts/server.py').then(() => {{
        showToast('已复制命令到剪贴板！');
      }});
    }});

    syncFilePickerBtn.addEventListener('click', () => {{
      markdownFileInput.click();
    }});

    markdownFileInput.addEventListener('change', (e) => {{
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {{
        const text = ev.target.result;
        parseAndApplyMarkdown(text);
        closeSyncModal();
        showToast(`✅ 已成功从 ${{file.name}} 读取并更新！`);
      }};
      reader.readAsText(file, 'utf-8');
    }});

    // 浏览器内置轻量 Markdown 表格解析器
    function parseAndApplyMarkdown(text) {{
      const lines = text.split(/\\r?\\n/).map(l => l.trim()).filter(l => l.startsWith('|') && !l.startsWith('|---'));
      if (lines.length < 2) return;

      const rows = lines.slice(1);
      const parsedCompanies = [];

      rows.forEach(r => {{
        const p = r.split('|').slice(1, -1).map(s => s.trim());
        if (p.length < 11) return;

        const comp = p[0];
        const code = p[1];
        const p_raw = p[2];
        const bear_raw = p[3];
        const base_raw = p[4];
        const bull_raw = p[5];
        const up_raw = p[6];
        const stance = p[7];
        const method = p[8];
        const cutoff = p[9];
        const rep_raw = p[10];

        const p_m = p_raw.match(/([\\d\\.]+)\\s*(港元|元)/);
        const price_val = p_m ? parseFloat(p_m[1]) : 0;
        const currency = p_m ? p_m[2] : '元';

        const d_m = p_raw.match(/(\\d{{4}}-\\d{{2}}-\\d{{2}})/);
        const price_date = d_m ? d_m[1] : '';

        const bear_m = bear_raw.match(/([\\d\\.]+)/);
        const bear_val = bear_m ? parseFloat(bear_m[1]) : 0;

        const base_m = base_raw.match(/([\\d\\.]+)/);
        const base_val = base_m ? parseFloat(base_m[1]) : 0;

        const bull_m = bull_raw.match(/([\\d\\.]+)/);
        const bull_val = bull_m ? parseFloat(bull_m[1]) : 0;

        const u_m = up_raw.match(/([+-]?[\\d\\.]+)%/);
        const upside_val = u_m ? parseFloat(u_m[1]) : 0;

        const rep_m = rep_raw.match(/\\((.*?)\\)/);
        const rep_link = rep_m ? rep_m[1] : '';
        const comp_dir = rep_link.split('/').slice(0, -1).join('/');

        let market = 'A股';
        if (code.includes('.HK')) market = code.includes('.SH') || code.includes('.SZ') ? 'A+H' : '港股';

        let stance_type = 'neutral';
        if (stance.includes('积极') || stance.includes('吸引力')) {{
          stance_type = stance.includes('偏积极') ? 'neutral_pos' : 'positive';
        }} else if (stance.includes('偏谨慎')) {{
          stance_type = 'cautious';
        }} else if (stance.includes('回避')) {{
          stance_type = 'avoid';
        }}

        // 保留已有争议摘要
        const old = DATASET.companies.find(c => c.company === comp);
        const thesis = old ? old.thesis : '';

        parsedCompanies.push({{
          company: comp,
          code: code,
          market: market,
          price_val: price_val,
          currency: currency,
          price_date: price_date,
          price_extra: p_raw.includes('停牌前') ? '停牌前' : (p_raw.includes('盘中') ? '盘中' : ''),
          price_raw: p_raw,
          bear_val: bear_val,
          bear_raw: bear_raw,
          base_val: base_val,
          base_raw: base_raw,
          bull_val: bull_val,
          bull_raw: bull_raw,
          upside_val: upside_val,
          upside_str: up_raw,
          stance: stance,
          stance_type: stance_type,
          method: method,
          cutoff_date: cutoff,
          report_link: rep_link,
          comp_dir: comp_dir,
          thesis: thesis,
          stance_weight: STANCE_ORDER[stance] || 99
        }});
      }});

      if (parsedCompanies.length > 0) {{
        DATASET.companies = parsedCompanies;
        render();
      }}
    }}

    function showToast(msg) {{
      toast.textContent = msg;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    }}

    // Init
    initTheme();
    render();
  </script>
</body>
</html>
"""
    return html_template


def sync_all():
    print(f"[1/3] 正在解析 {OVERVIEW_MD} ...")
    dataset = parse_overview_markdown()
    print(f" -> 成功解析 {len(dataset['companies'])} 家公司数据，最近更新时间: {dataset['last_updated']}")

    print(f"[2/3] 正在构建 HTML 交互式看板...")
    html_content = build_html_content(dataset)

    print(f"[3/3] 写入 {OUTPUT_HTML} ...")
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 若运行在 Antigravity 环境下，同步拷贝至当前会话 artifact 目录
    artifact_dir = r"C:\Users\13815\.gemini\antigravity\brain\55a9e595-5182-49d7-a5fc-861dda49fffc"
    if os.path.isdir(artifact_dir):
        try:
            import shutil
            shutil.copyfile(OUTPUT_HTML, os.path.join(artifact_dir, "stock-overview.html"))
        except Exception:
            pass

    print(f"[SUCCESS] 交互式网页构建完成: {OUTPUT_HTML}")
    return dataset


class SyncRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WORKSPACE_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/sync":
            try:
                dataset = sync_all()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                response = {
                    "status": "ok",
                    "message": "数据已成功同步！",
                    "data": dataset
                }
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                err_resp = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(err_resp, ensure_ascii=False).encode("utf-8"))
        else:
            self.send_error(404, "Endpoint Not Found")

    def do_GET(self):
        if self.path == "/api/sync":
            self.do_POST()
        elif self.path == "/" or self.path == "":
            self.send_response(302)
            self.send_header("Location", "/stock-overview.html")
            self.end_headers()
        else:
            super().do_GET()


def start_server(port=8080):
    server_address = ("", port)
    try:
        httpd = HTTPServer(server_address, SyncRequestHandler)
    except OSError:
        port = port + 1
        server_address = ("", port)
        httpd = HTTPServer(server_address, SyncRequestHandler)

    url = f"http://localhost:{port}/stock-overview.html"
    print("=" * 60)
    print(f"🚀 本地股票研究看板服务已启动！")
    print(f"🔗 访问地址: {url}")
    print(f"💡 在网页上点击【🔄 同步数据】按钮将直接触发数据同步脚本！")
    print("=" * 60)
    print("按 Ctrl+C 停止服务。")

    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止。")


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--serve", "-s", "serve"]:
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        sync_all()
        start_server(port)
    else:
        sync_all()
        print("\n💡 提示：若希望在网页看板中一键直接触发 Python 同步脚本，请运行：")
        print("    python scripts/sync_overview.py --serve")
        print("    或者直接运行: python scripts/server.py\n")


if __name__ == "__main__":
    main()
