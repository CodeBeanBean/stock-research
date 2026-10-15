#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitor.py
实时行情获取与估值基准偏差计算核心程序。
独立运行于 market-monitor 模块下，负责从 stock-overview.md 同步股票池并批量抓取
二级市场最新成交价，
并精准计算相对研究报告基准价格的偏差幅度、动态 Base 空间及扩张/收缩状态。
"""

import os
import sys
import re
import json
import urllib.request
from datetime import datetime

# 兼容 Windows GBK 控制台编码输出
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIR = os.path.join(MODULE_DIR, "cache")
SNAPSHOT_FILE = os.path.join(CACHE_DIR, "quotes_latest.json")
EXCLUSIONS_FILE = os.path.join(MODULE_DIR, "excluded_stocks.json")


def load_exclusions():
    """读取已剔除标的代码列表"""
    if os.path.exists(EXCLUSIONS_FILE):
        try:
            with open(EXCLUSIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("excluded_codes", [])
        except Exception:
            return []
    return []


def save_exclusions(excluded_codes, reason_map=None):
    """持久化保存已剔除标的清单"""
    if reason_map is None:
        reason_map = {}
    code_to_company = {s["code"]: s for s in STOCKS_POOL}
    # 也支持按公司名称反查代码
    name_to_code = {s["company"]: s["code"] for s in STOCKS_POOL}

    normalized_codes = []
    for c in excluded_codes:
        if c in name_to_code:
            c = name_to_code[c]
        normalized_codes.append(c)
    normalized_codes = list(dict.fromkeys(normalized_codes))

    items = []
    for c in normalized_codes:
        s = code_to_company.get(c, {})
        items.append({
            "code": c,
            "company": s.get("company", c),
            "market": s.get("market", ""),
            "excluded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason_map.get(c, "用户手动剔除")
        })

    data = {
        "excluded_codes": normalized_codes,
        "items": items,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(EXCLUSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data


# 历史回退池。正常情况下会在模块加载时由 stock-overview.md 动态覆盖。
STOCKS_POOL_FALLBACK = [
    {
        "company": "宝钢股份",
        "code": "600019.SH",
        "quote_sym": "sh600019",
        "market": "A股",
        "currency": "元",
        "base_price": 5.75,
        "base_date": "2026-09-07",
        "bear": 3.59,
        "base": 6.21,
        "bull": 9.55,
        "report_upside": 8.0,
        "stance": "中性观察",
        "method": "60% P/B + 40% 正常化归母 P/E"
    },
    {
        "company": "威高股份",
        "code": "01066.HK",
        "quote_sym": "hk01066",
        "market": "港股",
        "currency": "港元",
        "base_price": 3.23,
        "base_date": "2026-09-07",
        "bear": 2.40,
        "base": 4.89,
        "bull": 7.55,
        "report_upside": 51.4,
        "stance": "谨慎积极",
        "method": "正常化归母 P/E + 折价净现金"
    },
    {
        "company": "梦百合",
        "code": "603313.SH",
        "quote_sym": "sh603313",
        "market": "A股",
        "currency": "元",
        "base_price": 6.43,
        "base_date": "2026-09-04",
        "bear": 1.98,
        "base": 5.39,
        "bull": 9.83,
        "report_upside": -16.2,
        "stance": "中性偏谨慎",
        "method": "60% 正常化 P/E + 40% P/B"
    },
    {
        "company": "福寿园",
        "code": "01448.HK",
        "quote_sym": "hk01448",
        "market": "港股",
        "currency": "港元",
        "base_price": 2.64,
        "base_date": "2026-03-19",
        "bear": 0.76,
        "base": 1.31,
        "bull": 1.85,
        "report_upside": -50.5,
        "stance": "回避",
        "method": "2025H1 NAV治理与流动性压力折价，正常化P/E校验"
    },
    {
        "company": "信维通信",
        "code": "300136.SZ",
        "quote_sym": "sz300136",
        "market": "A股",
        "currency": "元",
        "base_price": 56.18,
        "base_date": "2026-09-04",
        "bear": 15.18,
        "base": 43.64,
        "bull": 81.63,
        "report_upside": -22.3,
        "stance": "中性偏谨慎",
        "method": "2028E扣非 P/E + 市场隐含预期校验"
    },
    {
        "company": "达势股份",
        "code": "01405.HK",
        "quote_sym": "hk01405",
        "market": "港股",
        "currency": "港元",
        "base_price": 30.50,
        "base_date": "2026-09-04",
        "bear": 17.19,
        "base": 40.67,
        "bull": 67.57,
        "report_upside": 33.3,
        "stance": "中性偏积极",
        "method": "70% 调整 P/E + 30%租赁调整 EV/EBITDA"
    },
    {
        "company": "保利物业",
        "code": "06049.HK",
        "quote_sym": "hk06049",
        "market": "港股",
        "currency": "港元",
        "base_price": 28.76,
        "base_date": "2026-09-04",
        "bear": 18.81,
        "base": 36.73,
        "bull": 57.89,
        "report_upside": 27.7,
        "stance": "谨慎积极",
        "method": "正常化 P/E + 折价可分配现金"
    },
    {
        "company": "中海物业",
        "code": "02669.HK",
        "quote_sym": "hk02669",
        "market": "港股",
        "currency": "港元",
        "base_price": 3.575,
        "base_date": "2026-09-04",
        "bear": 2.52,
        "base": 4.33,
        "bull": 6.21,
        "report_upside": 21.2,
        "stance": "中性观察",
        "method": "70% 正常化 P/E + 30% 股息资本化"
    },
    {
        "company": "天齐锂业",
        "code": "002466.SZ",
        "quote_sym": "sz002466",
        "market": "A股",
        "currency": "元",
        "base_price": 45.35,
        "base_date": "2026-09-04",
        "bear": 23.18,
        "base": 48.97,
        "bull": 76.00,
        "report_upside": 8.0,
        "stance": "中性观察",
        "method": "60% 正常化 P/E + 40% P/B"
    },
    {
        "company": "赣锋锂业",
        "code": "002460.SZ",
        "quote_sym": "sz002460",
        "market": "A股",
        "currency": "元",
        "base_price": 50.52,
        "base_date": "2026-09-04",
        "bear": 20.39,
        "base": 45.27,
        "bull": 74.35,
        "report_upside": -10.4,
        "stance": "中性偏谨慎",
        "method": "60% 正常化 P/E + 40% P/B"
    },
    {
        "company": "云铝股份",
        "code": "000807.SZ",
        "quote_sym": "sz000807",
        "market": "A股",
        "currency": "元",
        "base_price": 26.95,
        "base_date": "2026-09-04",
        "bear": 13.13,
        "base": 24.10,
        "bull": 39.06,
        "report_upside": -10.6,
        "stance": "中性观察",
        "method": "70% 正常化 P/E + 30% P/B"
    },
    {
        "company": "牧原股份",
        "code": "002714.SZ",
        "quote_sym": "sz002714",
        "market": "A股",
        "currency": "元",
        "base_price": 43.97,
        "base_date": "2026-09-04",
        "bear": 18.22,
        "base": 48.71,
        "bull": 81.26,
        "report_upside": 10.8,
        "stance": "中性观察",
        "method": "60% 正常化 P/E + 40% P/B"
    },
    {
        "company": "宝丰能源",
        "code": "600989.SH",
        "quote_sym": "sh600989",
        "market": "A股",
        "currency": "元",
        "base_price": 24.37,
        "base_date": "2026-09-01",
        "bear": 19.50,
        "base": 29.55,
        "bull": 41.41,
        "report_upside": 21.2,
        "stance": "谨慎积极",
        "method": "70% 正常化扣非 P/E + 30% EV/EBITDA"
    },
    {
        "company": "兆易创新",
        "code": "603986.SH",
        "quote_sym": "sh603986",
        "market": "A股",
        "currency": "元",
        "base_price": 393.00,
        "base_date": "2026-09-01",
        "bear": 249.18,
        "base": 447.10,
        "bull": 645.02,
        "report_upside": 13.8,
        "stance": "中性观察",
        "method": "正常化扣非 P/E + 折价金融投资"
    },
    {
        "company": "阳光电源",
        "code": "300274.SZ",
        "quote_sym": "sz300274",
        "market": "A股",
        "currency": "元",
        "base_price": 91.50,
        "base_date": "2026-08-31",
        "bear": 61.24,
        "base": 100.60,
        "bull": 144.35,
        "report_upside": 9.9,
        "stance": "中性偏积极",
        "method": "正常化 P/E，DCF 交叉验证"
    },
    {
        "company": "晋亿实业",
        "code": "601002.SH",
        "quote_sym": "sh601002",
        "market": "A股",
        "currency": "元",
        "base_price": 5.24,
        "base_date": "2026-08-27",
        "bear": 3.54,
        "base": 5.61,
        "bull": 7.89,
        "report_upside": 7.1,
        "stance": "中性偏积极",
        "method": "70% P/E + 30% P/B"
    },
    {
        "company": "百联股份",
        "code": "600827.SH",
        "quote_sym": "sh600827",
        "market": "A股",
        "currency": "元",
        "base_price": 7.78,
        "base_date": "2026-08-28",
        "bear": 4.59,
        "base": 7.35,
        "bull": 10.10,
        "report_upside": -5.5,
        "stance": "中性",
        "method": "60% P/B + 40% P/E"
    },
    {
        "company": "宋城演艺",
        "code": "300144.SZ",
        "quote_sym": "sz300144",
        "market": "A股",
        "currency": "元",
        "base_price": 5.97,
        "base_date": "2026-08-21",
        "bear": 3.42,
        "base": 5.36,
        "bull": 7.74,
        "report_upside": -10.2,
        "stance": "中性偏谨慎",
        "method": "70% P/E + 30% P/B"
    },
    {
        "company": "腾讯控股",
        "code": "0700.HK",
        "quote_sym": "hk00700",
        "market": "港股",
        "currency": "港元",
        "base_price": 461.60,
        "base_date": "2026-08-12",
        "bear": 478.00,
        "base": 629.00,
        "bull": 771.00,
        "report_upside": 36.0,
        "stance": "估值吸引力中等偏高",
        "method": "SOTP，DCF 交叉验证"
    },
    {
        "company": "三生制药",
        "code": "01530.HK",
        "quote_sym": "hk01530",
        "market": "港股",
        "currency": "港元",
        "base_price": 16.96,
        "base_date": "2026-08-28",
        "bear": 14.34,
        "base": 21.19,
        "bull": 30.97,
        "report_upside": 25.0,
        "stance": "谨慎积极",
        "method": "核心业务 P/E + 净现金 + 707 rNPV"
    },
    {
        "company": "海吉亚医疗",
        "code": "06078.HK",
        "quote_sym": "hk06078",
        "market": "港股",
        "currency": "港元",
        "base_price": 10.58,
        "base_date": "2026-08-28",
        "bear": 8.69,
        "base": 13.57,
        "bull": 17.83,
        "report_upside": 28.2,
        "stance": "谨慎积极",
        "method": "正常化 P/E"
    },
    {
        "company": "海底捞",
        "code": "06862.HK",
        "quote_sym": "hk06862",
        "market": "港股",
        "currency": "港元",
        "base_price": 11.41,
        "base_date": "2026-08-25",
        "bear": 8.32,
        "base": 12.52,
        "bull": 17.63,
        "report_upside": 9.7,
        "stance": "中性观察",
        "method": "70% P/E + 30% 股息资本化"
    },
    {
        "company": "中国民航信息网络",
        "code": "00696.HK",
        "quote_sym": "hk00696",
        "market": "港股",
        "currency": "港元",
        "base_price": 8.935,
        "base_date": "2026-08-25",
        "bear": 6.72,
        "base": 9.87,
        "bull": 13.17,
        "report_upside": 10.5,
        "stance": "中性偏积极",
        "method": "70% P/E + 30% P/B"
    }
]


def _select_quote_identity(company):
    """根据总览的价格币种，从 A/H 代码中选择与价格基准一致的行情代码。"""
    codes = [part.strip() for part in company["code"].split("/") if part.strip()]
    if not codes:
        raise ValueError(f"{company['company']} 缺少证券代码")

    if company["currency"] == "港元":
        selected = next((code for code in codes if code.endswith(".HK")), codes[0])
    else:
        selected = next((code for code in codes if code.endswith((".SH", ".SZ"))), codes[0])

    raw_code, suffix = selected.rsplit(".", 1)
    if suffix == "HK":
        return selected, f"hk{raw_code.zfill(5)}", "港股"
    if suffix == "SH":
        return selected, f"sh{raw_code}", "A股"
    if suffix == "SZ":
        return selected, f"sz{raw_code}", "A股"
    raise ValueError(f"暂不支持的证券代码: {selected}")


def load_stocks_pool():
    """从总览解析最新股票池；解析失败时保留历史回退池，避免服务不可用。"""
    scripts_dir = os.path.join(os.path.abspath(os.path.join(MODULE_DIR, "..")), "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    try:
        from sync_overview import parse_overview_markdown

        dataset = parse_overview_markdown()
        pool = []
        for company in dataset["companies"]:
            code, quote_sym, market = _select_quote_identity(company)
            pool.append({
                "company": company["company"],
                "code": code,
                "quote_sym": quote_sym,
                "market": market,
                "currency": company["currency"],
                "base_price": company["price_val"],
                "base_date": company["price_date"],
                "bear": company["bear_val"],
                "base": company["base_val"],
                "bull": company["bull_val"],
                "report_upside": company["upside_val"],
                "stance": company["stance"],
                "method": company["method"],
                "comp_dir": company["comp_dir"],
                "report_link": company["report_link"],
            })
        if not pool:
            raise ValueError("stock-overview.md 未解析出公司")
        return pool
    except Exception as exc:
        print(f"[Warning] 无法从 stock-overview.md 同步股票池，使用历史回退池: {exc}", file=sys.stderr)
        return STOCKS_POOL_FALLBACK


STOCKS_POOL = load_stocks_pool()


def fetch_raw_quotes(symbols):
    """
    通过腾讯财经接口批量抓取实时行情
    """
    url = f"http://qt.gtimg.cn/q={','.join(symbols)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            text = resp.read().decode("gbk", errors="ignore")
    except Exception as e:
        print(f"[Error] 获取行情失败: {e}", file=sys.stderr)
        return {}

    parsed = {}
    for line in text.strip().split(";"):
        line = line.strip()
        if not line:
            continue
        m = re.match(r'v_([a-z0-9]+)="([^"]*)"', line)
        if not m:
            continue
        sym = m.group(1)
        fields = m.group(2).split("~")
        if len(fields) < 5:
            continue

        try:
            latest_price = float(fields[3]) if fields[3] else 0.0
            prev_close = float(fields[4]) if fields[4] else 0.0
            today_open = float(fields[5]) if len(fields) > 5 and fields[5] else prev_close
            change_amount = float(fields[31]) if len(fields) > 31 and fields[31] else (latest_price - prev_close)
            change_pct = float(fields[32]) if len(fields) > 32 and fields[32] else 0.0
            high = float(fields[33]) if len(fields) > 33 and fields[33] else latest_price
            low = float(fields[34]) if len(fields) > 34 and fields[34] else latest_price
            quote_time = fields[30] if len(fields) > 30 else datetime.now().strftime("%Y%m%d%H%M%S")

            parsed[sym] = {
                "latest_price": latest_price,
                "prev_close": prev_close,
                "today_open": today_open,
                "change_amount": change_amount,
                "today_change_pct": change_pct,
                "high": high,
                "low": low,
                "quote_time": quote_time
            }
        except (ValueError, IndexError):
            continue

    return parsed


def parse_date(q_time):
    """
    解析行情时间戳中的交易日期 YYYY-MM-DD
    """
    if not q_time:
        return datetime.now().strftime("%Y-%m-%d")
    q_time = str(q_time).strip()
    if "/" in q_time:
        return q_time.split()[0].replace("/", "-")
    elif len(q_time) >= 8 and q_time[:8].isdigit():
        return f"{q_time[:4]}-{q_time[4:6]}-{q_time[6:8]}"
    return datetime.now().strftime("%Y-%m-%d")


def get_market_snapshot(excluded_codes=None):
    """
    拉取标的收盘行情并计算相对研报基准的偏差与三档动态估值空间
    """
    # 本地服务长期运行时也应读取最新目标价，避免沿用启动时的旧情景。
    global STOCKS_POOL
    STOCKS_POOL = load_stocks_pool()
    if excluded_codes is None:
        excluded_codes = load_exclusions()
    excluded_set = set(excluded_codes)

    symbols = [s["quote_sym"] for s in STOCKS_POOL]
    raw_quotes = fetch_raw_quotes(symbols)

    items = []

    for s in STOCKS_POOL:
        sym = s["quote_sym"]
        q = raw_quotes.get(sym)

        base_p = s["base_price"]
        bear = s["bear"]
        base = s["base"]
        bull = s["bull"]
        # 使用同一组 Base/基准价计算，避免 Markdown 的一位小数舍入制造虚假变化。
        report_upside = ((base - base_p) / base_p) * 100.0 if base_p else 0.0

        is_excluded = (s["code"] in excluded_set or s["company"] in excluded_set)

        if q and q["latest_price"] > 0:
            latest_p = q["latest_price"]
            today_change = q["today_change_pct"]
            q_time = q["quote_time"]
            close_d = parse_date(q_time)
            has_live = True
        else:
            latest_p = base_p
            today_change = 0.0
            q_time = datetime.now().strftime("%Y%m%d%H%M%S")
            close_d = s["base_date"]
            has_live = False

        # 偏差计算
        price_diff = latest_p - base_p
        price_diff_pct = (price_diff / base_p) * 100.0 if base_p else 0.0

        # 三档动态估值空间推算 (偏离目标价比例)
        dynamic_base_upside = ((base - latest_p) / latest_p) * 100.0 if latest_p else 0.0
        dynamic_bear_upside = ((bear - latest_p) / latest_p) * 100.0 if latest_p else 0.0
        dynamic_bull_upside = ((bull - latest_p) / latest_p) * 100.0 if latest_p else 0.0

        # 空间扩张/收敛幅度: 动态Base空间 - 报告Base空间
        delta_upside = dynamic_base_upside - report_upside
        if abs(delta_upside) < 1e-10:
            delta_upside = 0.0

        # 估值区间相对位置 (0=Bear, 1=Bull)
        range_span = bull - bear
        if range_span > 0:
            range_pos = (latest_p - bear) / range_span
        else:
            range_pos = 0.5

        # 状态预警标记
        if latest_p >= base:
            alert_status = "现价高于Base"
            alert_level = "warn"
        elif latest_p <= bear:
            alert_status = "跌破悲观估值"
            alert_level = "highlight"
        elif range_pos <= 0.25:
            alert_status = "逼近悲观估值"
            alert_level = "highlight"
        elif delta_upside >= 5.0:
            alert_status = "安全边际增厚"
            alert_level = "positive"
        elif delta_upside <= -5.0:
            alert_status = "空间明显收窄"
            alert_level = "cautious"
        else:
            alert_status = "基准窄幅震荡"
            alert_level = "normal"

        items.append({
            "company": s["company"],
            "code": s["code"],
            "quote_sym": s["quote_sym"],
            "market": s["market"],
            "currency": s["currency"],
            "base_price": base_p,
            "base_date": s["base_date"],
            "latest_price": latest_p,
            "close_price": latest_p,
            "close_date": close_d,
            "data_date": close_d,
            "today_change_pct": today_change,
            "price_diff": price_diff,
            "price_diff_pct": price_diff_pct,
            "price_diff_str": f"{'+' if price_diff >= 0 else ''}{price_diff:.3f}",
            "price_diff_pct_str": f"{'+' if price_diff >= 0 else ''}{price_diff_pct:.2f}%",
            "bear": bear,
            "base": base,
            "bull": bull,
            "report_upside": report_upside,
            "report_upside_str": f"{'+' if report_upside >= 0 else ''}{report_upside:.1f}%",
            "dynamic_base_upside": dynamic_base_upside,
            "dynamic_base_upside_str": f"{'+' if dynamic_base_upside >= 0 else ''}{dynamic_base_upside:.1f}%",
            "dynamic_bear_upside": dynamic_bear_upside,
            "dynamic_bear_upside_str": f"{'+' if dynamic_bear_upside >= 0 else ''}{dynamic_bear_upside:.1f}%",
            "dynamic_bull_upside": dynamic_bull_upside,
            "dynamic_bull_upside_str": f"{'+' if dynamic_bull_upside >= 0 else ''}{dynamic_bull_upside:.1f}%",
            "delta_upside": delta_upside,
            "delta_upside_str": f"{delta_upside:+.1f} 个百分点",
            "range_pos": range_pos,
            "alert_status": alert_status,
            "alert_level": alert_level,
            "stance": s["stance"],
            "method": s["method"],
            "comp_dir": s.get("comp_dir", ""),
            "report_link": s.get("report_link", ""),
            "quote_time": q_time,
            "has_live": has_live,
            "is_excluded": is_excluded
        })

    # KPI 统计基于活跃监控标的（剔除标的不干扰全库均值与极值）
    active_items = [i for i in items if not i["is_excluded"]]
    excluded_items = [i for i in items if i["is_excluded"]]

    active_live = [i for i in active_items if i["has_live"]]
    active_valid_count = len(active_live)
    active_total_diff = sum(i["price_diff_pct"] for i in active_live)
    avg_diff_pct = (active_total_diff / active_valid_count) if active_valid_count else 0.0

    valid_dates = [i["close_date"] for i in active_live]
    common_date = max(set(valid_dates), key=valid_dates.count) if valid_dates else datetime.now().strftime("%Y-%m-%d")
    now = datetime.now()
    is_intraday = common_date == now.strftime("%Y-%m-%d") and (now.hour, now.minute) < (16, 10)
    price_type = "盘中价" if is_intraday else "收盘价"

    gain_items = [i for i in active_items if i["price_diff_pct"] > 0]
    drop_items = [i for i in active_items if i["price_diff_pct"] < 0]
    flat_items = [i for i in active_items if i["price_diff_pct"] == 0]

    expanded = [i for i in active_items if i["delta_upside"] > 0]
    compressed = [i for i in active_items if i["delta_upside"] < 0]

    above_base = [i for i in active_items if i["latest_price"] >= i["base"]]
    below_bear = [i for i in active_items if i["latest_price"] <= i["bear"]]
    between_range = [i for i in active_items if i["bear"] < i["latest_price"] < i["base"]]

    max_gain = max(active_items, key=lambda x: x["price_diff_pct"]) if active_items else None
    max_drop = min(active_items, key=lambda x: x["price_diff_pct"]) if active_items else None

    kpis = {
        "total_count": len(items),
        "active_count": len(active_items),
        "excluded_count": len(excluded_items),
        "live_count": active_valid_count,
        "data_date": common_date,
        "price_type": price_type,
        "avg_diff_pct_str": f"{'+' if avg_diff_pct >= 0 else ''}{avg_diff_pct:.2f}%",
        "gain_count": len(gain_items),
        "drop_count": len(drop_items),
        "flat_count": len(flat_items),
        "expanded_count": len(expanded),
        "compressed_count": len(compressed),
        "above_base_count": len(above_base),
        "below_bear_count": len(below_bear),
        "between_range_count": len(between_range),
        "max_gain_text": f"{max_gain['company']} ({max_gain['price_diff_pct_str']})" if max_gain else "--",
        "max_drop_text": f"{max_drop['company']} ({max_drop['price_diff_pct_str']})" if max_drop else "--",
        "excluded_codes": list(excluded_set),
        "excluded_items": [{"code": i["code"], "company": i["company"], "market": i["market"]} for i in excluded_items],
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    result = {
        "kpis": kpis,
        "items": items
    }

    # 保存快照缓存
    os.makedirs(CACHE_DIR, exist_ok=True)
    try:
        with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    # 同步更新 market-dashboard.html 内嵌快照（保证纯本地文件打开时亦为最新快照）
    dashboard_html = os.path.join(MODULE_DIR, "market-dashboard.html")
    if os.path.exists(dashboard_html):
        try:
            with open(dashboard_html, "r", encoding="utf-8") as f:
                content = f.read()
            pattern = re.compile(r'const INITIAL_SNAPSHOT = \{.*?\};\n\s*let currentData', re.DOTALL)
            replacement = f"const INITIAL_SNAPSHOT = {json.dumps(result, ensure_ascii=False)};\n    let currentData"
            if pattern.search(content):
                new_content = pattern.sub(replacement, content, count=1)
                with open(dashboard_html, "w", encoding="utf-8") as f:
                    f.write(new_content)
        except Exception:
            pass

    return result


def print_cli_table(snapshot, show_all=False):
    """
    终端精美表格打印 (展示活跃监控标的，支持 --all 查看全量)
    """
    kpis = snapshot["kpis"]
    items = snapshot["items"]

    print("=" * 132)
    print("📊  股票研究标的池 · 收盘行情与估值基准偏差监控 (Market Monitor)")
    print(f"📅  数据日期: {kpis['data_date']} ({kpis['price_type']})  |  更新时间: {kpis['updated_at']}")
    print(f"🏢  标的规模: 活跃监控 {kpis['active_count']}/{kpis['total_count']} 家  |  已剔除: {kpis['excluded_count']} 家")
    print(f"📈  活跃平均偏离: {kpis['avg_diff_pct_str']}  |  最大上涨: {kpis['max_gain_text']}  |  最大回调: {kpis['max_drop_text']}")
    print(f"🛡️  空间扩张(增厚): {kpis['expanded_count']} 家  |  空间收窄: {kpis['compressed_count']} 家  |  高于Base: {kpis['above_base_count']} 家  |  破Bear: {kpis['below_bear_count']} 家")
    if kpis['excluded_count'] > 0:
        ex_names = ", ".join([f"{i['company']}({i['code']})" for i in kpis['excluded_items']])
        print(f"🚫  已剔除标的: {ex_names} [使用 python monitor.py --all 查看全量]")
    print("=" * 132)

    header_fmt = "{:<8} {:<10} {:>9} {:<10} {:>7} {:>9} {:>13} {:>10} {:>10} {:>10} {:>8} {:<10}"
    row_fmt    = "{:<8} {:<10} {:>9.2f} {:<10} {:>6.2f}% {:>9.2f} {:>13} {:>10} {:>10} {:>10} {:>8} {:<10}"

    print(header_fmt.format("公司", "代码", "收盘价", "数据日期", "日涨跌", "基准价", "基准偏离(ΔP%)", "动态Base", "动态Bear", "动态Bull", "空间Δ", "状态预警"))
    print("-" * 132)

    display_items = items if show_all else [i for i in items if not i["is_excluded"]]
    sorted_items = sorted(display_items, key=lambda x: x["price_diff_pct"], reverse=True)

    for i in sorted_items:
        status_label = i["alert_status"]
        if i["is_excluded"]:
            status_label = "[已剔除]"
        print(row_fmt.format(
            i["company"][:4],
            i["code"],
            i["latest_price"],
            i["close_date"],
            i["today_change_pct"],
            i["base_price"],
            i["price_diff_pct_str"],
            i["dynamic_base_upside_str"],
            i["dynamic_bear_upside_str"],
            i["dynamic_bull_upside_str"],
            i["delta_upside_str"],
            status_label
        ))

    print("=" * 132)


def main():
    args = sys.argv[1:]

    if "--exclude" in args:
        idx = args.index("--exclude")
        if idx + 1 < len(args):
            target = args[idx + 1]
            ex = load_exclusions()
            match_code = None
            match_name = None
            for s in STOCKS_POOL:
                if target in (s["code"], s["company"], s["quote_sym"]):
                    match_code = s["code"]
                    match_name = s["company"]
                    break
            if match_code:
                if match_code not in ex:
                    ex.append(match_code)
                    save_exclusions(ex)
                    print(f"✅ 已成功剔除标的: {match_name} ({match_code})")
                else:
                    print(f"ℹ️ 标的 {match_name} ({match_code}) 已经处于剔除状态。")
            else:
                print(f"❌ 未找到匹配标的: {target}")
        else:
            print("用法: python monitor.py --exclude <代码或名称>")
        snapshot = get_market_snapshot()
        print_cli_table(snapshot)
        return

    if "--restore" in args or "--include" in args:
        opt = "--restore" if "--restore" in args else "--include"
        idx = args.index(opt)
        if idx + 1 < len(args):
            target = args[idx + 1]
            ex = load_exclusions()
            match_code = None
            match_name = None
            for s in STOCKS_POOL:
                if target in (s["code"], s["company"], s["quote_sym"]):
                    match_code = s["code"]
                    match_name = s["company"]
                    break
            if match_code:
                if match_code in ex:
                    ex.remove(match_code)
                    save_exclusions(ex)
                    print(f"✅ 已成功加回标的: {match_name} ({match_code})")
                else:
                    print(f"ℹ️ 标的 {match_name} ({match_code}) 不在剔除列表中。")
            else:
                print(f"❌ 未找到匹配标的: {target}")
        else:
            print("用法: python monitor.py --restore <代码或名称>")
        snapshot = get_market_snapshot()
        print_cli_table(snapshot)
        return

    if "--exclusions" in args:
        ex = load_exclusions()
        print("=" * 60)
        print(f"🚫 当前已剔除标的清单 (共 {len(ex)} 家):")
        if not ex:
            print("  (暂无被剔除标的)")
        else:
            code_map = {s["code"]: s["company"] for s in STOCKS_POOL}
            for c in ex:
                print(f"  - {code_map.get(c, '未知标的')} ({c})")
        print("=" * 60)
        return

    show_all = ("--all" in args)
    snapshot = get_market_snapshot()

    if "--json" in args:
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))
    else:
        print_cli_table(snapshot, show_all=show_all)


if __name__ == "__main__":
    main()
