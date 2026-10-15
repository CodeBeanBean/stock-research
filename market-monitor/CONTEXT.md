# Market Monitor 实时行情与估值偏差监控系统上下文

**最后更新：** 2026-10-13  
**工作区：** `d:\Research\stock-research\market-monitor`  
**模块定位：** 实时行情获取、价格偏差追踪与动态估值空间监控子系统  
**上下文隔离声明：** 本文件是市场行情与价格变动监控的独立上下文，**严格独立维护**，不与基本面深度研究档案（`PROJECT_CONTEXT.md`）混同。基本面报告的财务数据与静态估值模型保持其发布时的经审计严肃性，本模块仅追踪二级市场价格相对基准的动态漂移。

---

## 1. 系统目标与核心职责

1. **标的池映射**：每次运行动态承接 `stock-overview.md` 中的全量公司；新增、删除或更新总览后无需再手工维护看板常量。
2. **行情与交易日核验**：基于腾讯财经接口获取各标的最新行情价（内部字段 `close_price`）与交易数据日期（`close_date` / `data_date`），交易时段内标记为盘中价，收市后标记为收盘价。
3. **全维度估值基准偏差计算（Deviation Metrics）**：
   - 追踪收盘价相对研报发布基准日价格的**基准偏差绝对额与偏离比例**（$\Delta P$ 及 $\Delta P\%$）。
   - 基于研报设定的 Bear / Base / Bull 三档估值，推导**三档动态偏离空间**（距 Bear、距 Base、距 Bull），衡量安全边际是随着回调增厚、还是随着冲高被压缩。
4. **看板展示与预警**：
   - 提供独立交互看板（`market-dashboard.html`），内置最新离线快照；排行使用 auto-fit 根据容器宽度自动增减列数，每项最小宽度 320px，宽屏可显示 3—5 列；默认前 8 家，明确显示数值与前后对比，可展开全部。
   - 提供命令行工具（`monitor.py`）与按需本地服务（`server.py`）。

---

## 2. 标的池与行情代码映射规范

- 唯一的标的池数据源是根目录 `stock-overview.md`，由 `scripts/sync_overview.py` 的解析逻辑读取公司名、市场代码、币种、基准价和 Bear / Base / Bull。
- A 股代码根据 `.SH` / `.SZ` 映射为腾讯行情的 `sh` / `sz` 前缀；港股根据 `.HK` 补齐为五位数并添加 `hk` 前缀。
- 若公司同时有 A/H 股，优先按总览中的估值币种选择对应报价；无法判定时回退到第一个可用代码。
- 公司目录和研报链接也从总览同步，以确保看板“查看研报”链接不依赖中文名推断。

---

## 3. 偏差指标数学定义与全维比例体系

设标的 $i$：
- 报告基准价格：$P_{\text{base}}$（附发布日期 $D_{\text{base}}$）
- 研报静态基准空间：$\text{Upside}_{\text{report}} = \frac{\text{Base} - P_{\text{base}}}{P_{\text{base}}}$
- 最新收盘价格：$P_{\text{close}}$（附数据交易日期 $D_{\text{close}}$）

指标计算如下：
1. **价格偏差绝对额**：
   $$\text{Price Diff} = P_{\text{close}} - P_{\text{base}}$$
2. **基准价格偏离比例（ΔP%）**：
   $$\Delta P\% = \frac{P_{\text{close}} - P_{\text{base}}}{P_{\text{base}}} \times 100\%$$
   - 正值（绿色）：现价高于研报发布日基准价；负值（红色）：现价回调低于研报基准日。
3. **三档动态估值偏离空间**：
   - **动态 Base 偏离空间**：$\text{Dynamic Base Upside} = \frac{\text{Base} - P_{\text{close}}}{P_{\text{close}}} \times 100\%$
   - **动态 Bear 偏离空间**：$\text{Dynamic Bear Upside} = \frac{\text{Bear} - P_{\text{close}}}{P_{\text{close}}} \times 100\%$
   - **动态 Bull 偏离空间**：$\text{Dynamic Bull Upside} = \frac{\text{Bull} - P_{\text{close}}}{P_{\text{close}}} \times 100\%$
4. **估值空间扩张度（Delta Upside）**：
   $$\Delta \text{Upside} = \text{Dynamic Base Upside} - \text{Upside}_{\text{report}}$$
   - 两项空间都使用同一个 Base 目标与未舍入价格计算，差值单位为**百分点**；不直接用 Markdown 已舍入的一位小数参与减法。
   - 前端从原始 Bear/Base/Bull 目标和最新价重算派生字段，覆盖内嵌快照、缓存和 API 入口；三档空间及正负颜色必须一一对应。
   - Base 排行显示“最新价 → Base目标”，动态 Base 列附目标值和公式提示；CSV 同时导出三档目标以便复核。
   - $\Delta \text{Upside} > 0$：表示股价回调导致基准潜在上涨空间扩大（安全边际增厚）；
   - $\Delta \text{Upside} < 0$：表示股价上涨冲高导致基准潜在空间被压缩。
5. **动态区间位置（Range Position）**：
   $$\text{Position} = \frac{P_{\text{close}} - \text{Bear}}{\text{Bull} - \text{Bear}}$$
   - $\le 0$：跌破悲观估值，极限安全边际或需核查基本面风险；
   - $0 \sim 0.25$：逼近悲观估值；
   - $0.25 \sim 1.0$：处于估值合理区间；
   - $\ge 1.0$：超越乐观估值。

---

## 4. 文件组织与接口定义

```text
market-monitor/
├─ CONTEXT.md                  # 本文件，市场监控独立上下文（严格隔离）
├─ README.md                   # 模块使用与快速上手说明
├─ monitor.py                  # 核心程序：收盘行情、日期解析、全维偏离比、剔除管理与 CLI 呈现
├─ server.py                   # 本地 HTTP API 服务，支撑按需手动核验与标的池剔除同步
├─ excluded_stocks.json        # 独立配置文件：维护用户剔除标的清单及剔除原因/时间戳
├─ market-dashboard.html       # 独立看板前端：自适应多列排行、标的池管理弹窗、剔除/加回、CSV 导出
└─ cache/                      # 最新收盘快照持久化缓存
   └─ quotes_latest.json
```

### HTTP API 接口规范

- `GET /api/quotes`：返回标的最新收盘行情与偏差计算 JSON（包含活跃标的 KPI 与剔除统计）。
- `POST /api/quotes` 或 `POST /api/refresh`：按需重新拉取最新收盘价并刷新快照。
- `GET /api/exclusions`：获取当前剔除的标的代码列表、原因及更新时间。
- `POST /api/exclusions`：修改剔除列表，支持操作格式：
  ```json
  {
    "action": "exclude" | "restore" | "clear" | "set",
    "codes": ["01448.HK"],
    "reasons": { "01448.HK": "基本面逻辑发生根本变化" }
  }
  ```

---

## 5. 标的池剔除与加回机制（Exclusion & Restore）

在日常市场跟踪中，部分标的可能出现基本面重大变化、长期停牌、或研究员暂时不需要跟踪的情况。为避免被剔除标的之极端负偏差扭曲整个标的池的统计基准，系统设计了完备的剔除与加回机制：

1. **KPI 统计隔离原则**：
   - 全库宏观 KPI（平均偏离比例、最大涨跌幅、估值空间扩张/收缩数量、高于 Base / 跌破 Bear 家数）**严格仅基于活跃标的（Active Stocks）计算**；
   - 被剔除标的（Excluded Stocks）在全景表格中提供专属视觉标识（浅灰背景、划线样式及【↩️ 加回】快捷按钮），默认可在看板中通过“活跃 / 全部 / 已剔除”筛选胶囊自由切换显示。
2. **多端交互与持久化**：
   - **CLI 命令行**：
     - `python market-monitor/monitor.py --exclude <代码或名称>`：剔除标的
     - `python market-monitor/monitor.py --restore <代码或名称>`：加回标的
     - `python market-monitor/monitor.py --exclusions`：查看已剔除清单
     - `python market-monitor/monitor.py --all`：强制在终端展示全量（包含已剔除）标的
   - **网页交互看板**：
     - 顶栏常驻【⚙️ 标的池管理 (N)】按钮，点击唤起管理弹窗，支持分类查看、一键清空全部加回；
     - 每一行数据操作列与抽屉卡片均配备【🚫 剔除】/【↩️ 加回】按键；
     - 双模持久化：优先走 `/api/exclusions` 后端服务保存至 `excluded_stocks.json`；若离线 `file:///` 打开，则自动平滑降级至浏览器的 `localStorage`，确保剔除状态永不丢失。

---

## 6. 维护与更新原则

1. **隔离性**：市场监控程序产生的数据快照、剔除配置与缓存只保留在 `market-monitor/` 内部，绝不向根目录或 `companies/` 写入临时行情，严禁污染 `PROJECT_CONTEXT.md`。
2. **收盘与日期标记**：不使用无休止的实时秒级轮询，严格标注各标的与全库的数据日期（如 `2026-09-09` 收盘）。
3. **偏离比例显式性**：无论是图表还是表格，所有偏离比例（基准偏离、动态 Base、动态 Bear、动态 Bull、空间变化）均保证 100% 显式呈现，杜绝因条形宽度导致隐藏漏显。
