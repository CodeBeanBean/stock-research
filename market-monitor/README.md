# Market Monitor · 标的行情与估值基准偏差监控

这是一个独立于公司基本面深度研究档案的市场行情监控子系统。标的池从根目录 `stock-overview.md` 动态同步，当前覆盖 30 家公司；系统跟踪最新**行情价**，并计算相对研报发布基准日的**基准价格偏离比例**以及由此推演的**三档估值动态空间（Bear / Base / Bull）**。

> 📌 **上下文隔离说明**：本模块的所有运行逻辑、代码映射及维护规范均独立保存在本目录下的 [`CONTEXT.md`](CONTEXT.md)，**严格不与基本面研究上下文（`PROJECT_CONTEXT.md`）混同**。

---

## 核心功能

1. **标的行情核验与数据日期标记**：
   - 自动读取 `stock-overview.md` 的全量标的，抓取最新行情价（内部字段 `close_price`）并标注交易数据日期。
   - 交易时段内标记为“盘中价”，收市后标记为“收盘价”；不做秒级轮询，仅按需刷新核验。
2. **全维度偏差计算（Deviation Metrics）**：
   - **偏差绝对额**：$\text{Price Diff} = P_{\text{收盘}} - P_{\text{基准}}$
   - **基准偏离比例 (ΔP%)**：$\text{Price Diff \%} = \frac{P_{\text{收盘}} - P_{\text{基准}}}{P_{\text{基准}}} \times 100\%$
   - **动态 Base 偏离空间**：$\text{Dynamic Base Upside} = \frac{\text{Base} - P_{\text{收盘}}}{P_{\text{收盘}}} \times 100\%$
   - **三档动态估值空间**：同步计算距 Bear 悲观、距 Base 基准、距 Bull 乐观的偏离空间。
   - **空间扩张度 ($\Delta$)**：动态 Base 空间减去报告 Base 空间，单位为**百分点**。两项空间均从目标价与价格计算后再显示舍入结果，避免舍入造成虚假变化。
3. **优化交互式看板（market-dashboard.html）**：
   - **紧凑排行**：根据容器宽度自动增减列数，每项最小宽度 320px，宽屏可显示 3—5 列；展示排名、公司、关键数值和前后对比，默认前 8 家，可展开全部；
   - **标的池动态管理（剔除与加回）**：
     - 顶栏常驻【⚙️ 标的池管理】快捷入口与弹窗，支持已剔除列表与活跃搜索，支持一键全部加回；
     - 表格操作列支持单键【🚫 剔除】与【↩️ 加回】；
     - 过滤栏支持【活跃标的】/【全部标的】/【已剔除】快速切换；
     - 动态重算 KPI，确保全库均值与极值只统计有效活跃标的；
   - **三重视角切换**：支持基准价偏离率 (ΔP%)、动态 Base 空间、空间扩张度 (Δ) 一键切换排行；
   - **公司详情抽屉**：点击表格行或排行项，滑出抽屉查看三档目标价与偏离深度；
   - **CSV 导出**：一键导出包含行情日期、基准日期、剔除状态与全套偏离指标的数据表。

---

## 快速启动与使用

### 1. 终端命令行快速查看与标的池管理

在终端直接运行：
```powershell
# 1. 默认仅展示活跃标的监控表与活跃 KPI
python market-monitor/monitor.py

# 2. 剔除指定标的（支持股票代码、接口代码或公司中文名）
python market-monitor/monitor.py --exclude 01448.HK
python market-monitor/monitor.py --exclude 福寿园

# 3. 加回指定标的
python market-monitor/monitor.py --restore 01448.HK

# 4. 查看当前已剔除标的清单
python market-monitor/monitor.py --exclusions

# 5. 强制查看全量标的（含被剔除标的）
python market-monitor/monitor.py --all

# 6. 输出标准 JSON 格式数据
python market-monitor/monitor.py --json
```

### 2. 离线/直接打开看板（免启动服务）

直接在浏览器中双击或打开：
```text
file:///D:/Research/stock-research/market-monitor/market-dashboard.html
```
*已内置最新行情快照并支持 `localStorage` 本地保存剔除清单，双击即可无缝浏览、排序、筛选、剔除加回及导出。*

### 3. 启动本地看板服务（支持联机与按需核验）

在项目根目录下运行：
```powershell
python market-monitor/server.py
```
- 浏览器将打开：`http://localhost:8090/market-monitor/market-dashboard.html`
- 网页右上角可随时点击【🔄 刷新行情】即时核对最新价格。
- 标的剔除与加回操作将自动同步保存至本地 `excluded_stocks.json`。

---

## 目录结构

```text
market-monitor/
├─ CONTEXT.md                  # 独立维护的监控系统专属上下文（严格隔离）
├─ README.md                   # 本文件，系统功能与使用说明
├─ monitor.py                  # 核心程序：收盘行情抓取、日期解析、偏差计算、剔除管理与终端打印
├─ server.py                   # 本地 HTTP API 服务（提供 /api/quotes 与 /api/exclusions）
├─ excluded_stocks.json        # 独立配置文件：维护标的剔除清单、原因及时间戳
├─ market-dashboard.html       # 交互式行情监控看板前端（偏离比例完整展示 + 标的池管理）
└─ cache/                      # 最新收盘快照持久化缓存
   └─ quotes_latest.json
```
