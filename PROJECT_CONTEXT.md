# Stock Research 项目长期上下文与会话交接

**最后更新：** 2026-09-08
**工作区：** `D:\Research`  
**研究库：** `D:\Research\stock-research`  
**当前状态：** 23 家上市公司已建立档案；宝钢股份为最新完成的公司

## 本文件的用途

本文件保存跨会话需要继续使用的项目事实、工作约定和当前研究状态。它不是完整聊天记录，也不是财务事实的一级来源。新会话应先读取本文件、[估值总览](stock-overview.md)和目标公司的现有档案，再根据最新正式披露开展增量工作。

Codex 会在新任务开始时读取适用范围内的 `AGENTS.md`。项目已在 `D:\Research\AGENTS.md` 和本目录的 `AGENTS.md` 配置启动规则，使新会话能够自动发现本文件。普通 Markdown 如果没有被 `AGENTS.md` 指向，并不保证会被新会话主动读取。

## 项目形成过程中的持久决定

1. 股票研究项目的正式位置是 `D:\Research\stock-research`。早期文件曾误写入 `D:\wxProj`，现已明确禁止再次写入或迁回该目录。
2. 每家公司使用独立目录，并保留报告、公司档案、财务模型、来源索引、更新记录和原始披露。
3. 股票分析和财报更新使用本机 `equity-research` skill；财务模型使用 `spreadsheets` skill 的可复核、渲染和验收流程。
4. 新建公司或进行重大财报/估值更新后，必须同步更新全库 [股票研究估值总览](stock-overview.md)。这一规则已经写入 `equity-research` skill。
5. 晋亿实业的早期模型 Cover 缺少图表，用户要求修正。此后所有公司模型的 Cover 都应包含有决策价值的图表，例如收入结构、历史趋势或情景价值与当前价格比较。
6. 研究结论必须区分事实、管理层表述、研究计算和分析假设；至少给出 Bear/Base/Bull，并写明最强反方和证伪条件。
7. 价格、股本、汇率、财报和估值均需标明日期。总览不是实时行情表，旧值不能直接当作当前值。

## 当前目录结构

```text
D:\Research\
├─ AGENTS.md                         # 工作区级自动加载说明
└─ stock-research\
   ├─ AGENTS.md                      # 股票研究专用规则
   ├─ PROJECT_CONTEXT.md             # 本文件，跨会话长期上下文
   ├─ README.md                      # 项目说明与覆盖状态
   ├─ stock-overview.md              # 估值总览和报告导航
   ├─ stock-overview.html            # 交互式估值看板网页（多字段排序/筛选/图表）
   ├─ scripts/                       # 核心业务脚本与工具
   │  ├─ sync_overview.py            # 数据同步与看板构建脚本
   │  └─ server.py                   # 本地轻量服务（支持网页端一键同步）
   ├─ companies\<company>\
   │  ├─ company-profile.md
   │  ├─ research-report.md
   │  ├─ financial-model.xlsx
   │  ├─ source-index.md
   │  ├─ update-log.md
   │  └─ source-documents\
   ├─ outputs\<research-run>\        # 模型和视觉验收产物
   └─ .work\                         # 可复现脚本与临时依赖
```

## 当前覆盖与估值快照

以下数据来自 2026-09-08 的 [stock-overview.md](stock-overview.md)，仅用于接续定位。后续分析应以各公司报告、模型和最新披露为准。

| 公司 | 代码 | 价格基准 | Bear | Base | Bull | 当前判断 | 资料截止 | 档案 |
|---|---|---:|---:|---:|---:|---|---|---|
| 宝钢股份 | 600019.SH | 5.75 元 | 3.59 元 | 6.21 元 | 9.55 元 | 中性观察 | 2026-09-08 | [报告](companies/baosteel/research-report.md) |
| 威高股份 | 01066.HK | 3.23 港元 | 2.40 港元 | 4.89 港元 | 7.55 港元 | 谨慎积极 | 2026-09-08 | [报告](companies/weigao-group/research-report.md) |
| 梦百合 | 603313.SH | 6.43 元 | 1.98 元 | 5.39 元 | 9.83 元 | 中性偏谨慎 | 2026-09-07 | [报告](companies/mlily/research-report.md) |
| 福寿园 | 01448.HK | 2.64 港元（停牌前） | 0.76 港元 | 1.31 港元 | 1.85 港元 | 回避 | 2026-09-07 | [报告](companies/fu-shou-yuan/research-report.md) |
| 信维通信 | 300136.SZ | 56.18 元 | 15.18 元 | 43.64 元 | 81.63 元 | 中性偏谨慎 | 2026-09-07 | [报告](companies/sunway-communication/research-report.md) |
| 达势股份 | 01405.HK | 30.50 港元 | 17.19 港元 | 40.67 港元 | 67.57 港元 | 中性偏积极 | 2026-09-07 | [报告](companies/dpc-dash/research-report.md) |
| 保利物业 | 06049.HK | 28.76 港元 | 18.81 港元 | 36.73 港元 | 57.89 港元 | 谨慎积极 | 2026-09-06 | [报告](companies/poly-property-services/research-report.md) |
| 中海物业 | 02669.HK | 3.575 港元 | 2.52 港元 | 4.33 港元 | 6.21 港元 | 中性观察 | 2026-09-06 | [报告](companies/china-overseas-property/research-report.md) |
| 天齐锂业 | 002466.SZ / 09696.HK | 45.35 元 | 23.18 元 | 48.97 元 | 76.00 元 | 中性观察 | 2026-09-05 | [报告](companies/tianqi-lithium/research-report.md) |
| 赣锋锂业 | 002460.SZ / 01772.HK | 50.52 元 | 20.39 元 | 45.27 元 | 74.35 元 | 中性偏谨慎 | 2026-09-05 | [报告](companies/ganfeng-lithium/research-report.md) |
| 云铝股份 | 000807.SZ | 26.95 元 | 13.13 元 | 24.10 元 | 39.06 元 | 中性观察 | 2026-09-05 | [报告](companies/yunnan-aluminum/research-report.md) |
| 牧原股份 | 002714.SZ / 02714.HK | 43.97 元 | 18.22 元 | 48.71 元 | 81.26 元 | 中性观察 | 2026-09-05 | [报告](companies/muyuan/research-report.md) |
| 宝丰能源 | 600989.SH | 24.37 元 | 19.50 元 | 29.55 元 | 41.41 元 | 谨慎积极 | 2026-09-02 | [报告](companies/baofeng-energy/research-report.md) |
| 兆易创新 | 603986.SH | 393.00 元 | 249.18 元 | 447.10 元 | 645.02 元 | 中性观察 | 2026-09-02 | [报告](companies/gigadevice/research-report.md) |
| 阳光电源 | 300274.SZ | 91.50 元 | 61.24 元 | 100.60 元 | 144.35 元 | 中性偏积极 | 2026-09-01 | [报告](companies/sungrow/research-report.md) |
| 晋亿实业 | 601002.SH | 5.24 元 | 3.54 元 | 5.61 元 | 7.89 元 | 中性偏积极 | 2026-08-27 | [报告](companies/jinyi-industrial/research-report.md) |
| 百联股份 | 600827.SH | 7.78 元 | 4.59 元 | 7.35 元 | 10.10 元 | 中性 | 2026-08-29 | [报告](companies/bailian/research-report.md) |
| 宋城演艺 | 300144.SZ | 5.97 元 | 3.42 元 | 5.36 元 | 7.74 元 | 中性偏谨慎 | 2026-08-24 | [报告](companies/songcheng-performance/research-report.md) |
| 腾讯控股 | 0700.HK | 461.60 港元 | 478 港元 | 629 港元 | 771 港元 | 估值吸引力中等偏高 | 2026-08-12 | [报告](companies/tencent/research-report.md) |
| 三生制药 | 01530.HK | 16.96 港元 | 14.34 港元 | 21.19 港元 | 30.97 港元 | 谨慎积极 | 2026-08-31 | [报告](companies/3sbio/research-report.md) |
| 海吉亚医疗 | 06078.HK | 10.58 港元 | 8.69 港元 | 13.57 港元 | 17.83 港元 | 谨慎积极 | 2026-08-30 | [报告](companies/hygeia-healthcare/research-report.md) |
| 海底捞 | 06862.HK | 11.41 港元 | 8.32 港元 | 12.52 港元 | 17.63 港元 | 中性观察 | 2026-08-26 | [报告](companies/haidilao/research-report.md) |
| 中国民航信息网络 | 00696.HK | 8.935 港元 | 6.72 港元 | 9.87 港元 | 13.17 港元 | 中性偏积极 | 2026-08-26 | [报告](companies/travelsky/research-report.md) |

价格基准日期并不完全相同，详见总览和各公司报告。不能根据表中“Base 相对价格”脱离业务质量、盈利可见度和证伪条件做机械排名。

## 已完成的主要工作

- 宝钢股份：首次档案及2026H1分析；核心争议是高端产品和出口增长能否抵消矿焦涨价与钢价偏弱，以及马钢有限、山钢日照近200亿元联营投资能否提升回报。
- 威高股份：首次档案及2026H1分析；核心争议是集采后的毛利底、关联方应收质量，以及威高普瑞置入威高血净后归母利润和现金流能否真正增厚。
- 梦百合：首次档案及2026H1分析；核心争议是全球制造与线上增长能否转化为利润，以及关联方应收、业绩预告更正和审计保留意见能否完成治理修复。
- 福寿园：首次档案及停牌特殊情形分析；核心争议是2016—2025年存疑交易是否扩大、2025年报和2026年中报能否补发、管理层诚信与内控能否满足复牌指引，以及新规下墓位ASP能否企稳。
- 信维通信：首次档案及2026H1分析；核心争议是商业卫星、AI硬件、汽车和MLCC能否覆盖60亿元定增摊薄、11亿元并购、折旧和资本开支，并形成每股自由现金流增长。
- 腾讯控股：首次公司档案、基本面分析和 SOTP/DCF 估值。
- 百联股份：首次分析，后续已按中报更新数据与估值。
- 晋亿实业：首次分析，后续已按中报更新；模型 Cover 图表问题已修复。
- 宋城演艺：首次分析并完成最新中报更新。
- 海底捞：中国香港上市餐饮公司首次分析及中期业绩分析。
- 中国民航信息网络：首次分析及中期业绩分析。
- 海吉亚医疗：首次分析，后续已按中报更新。
- 三生制药：首次分析，估值包含核心业务、净现金和 707 项目 rNPV。
- 阳光电源：首次分析，采用正常化 P/E，DCF 交叉验证。
- 兆易创新：首次档案及 2026H1 分析；核心争议是存储高毛利和公允价值收益的可持续性。
- 宝丰能源：首次档案及 2026H1 分析；核心争议是高价差能否延续。
- 牧原股份：首次档案及 2026H1 分析；核心争议是成本领先能否抵消猪价长期低迷和资产负债表压力。
- 天齐锂业：首次档案及 2026H1 分析；核心争议是锂价正常化、SQM 权益现金回流和海外项目资本效率。
- 赣锋锂业：首次档案及 2026H1 分析；核心争议是多项目选择权能否转化为自由现金流并降低净债务。
- 云铝股份：首次档案及 2026H1 分析；核心争议是高铝价、水电利用率和高分红的可持续性。
- 保利物业：首次档案及 2026H1 分析；核心争议是第三方扩张的单位经济性、应收款增长和净现金兑现。
- 中海物业：首次档案及 2026H1 分析；核心争议是清退低效项目能否带来利润率和回款修复。
- 达势股份：首次档案及 2026H1 分析；核心争议是平台补贴驱动的交易增长能否转化为 ATP、SSSG、利润率和租赁后自由现金流修复，以及 2027 年主特许经营权能否顺利续约。

## 本次会话最新成果：宝钢股份

### 文件

- [公司档案](companies/baosteel/company-profile.md)
- [基本面研究报告](companies/baosteel/research-report.md)
- [财务模型](companies/baosteel/financial-model.xlsx)
- [来源索引](companies/baosteel/source-index.md)
- [更新记录](companies/baosteel/update-log.md)

### 研究结论

- 价格基准为2026-09-07收盘5.75元；当前判断为中性观察，业务质量中上、盈利可见度中低、估值置信度中。
- 2026H1收入1,607.31亿元、归母净利润45.71亿元，分别同比增长6.2%和下降6.3%；钢铁制造毛利率降至4.9%，购销价差是当前盈利压力核心。
- 2026H1经营现金流148.15亿元、简化自由现金流56.31亿元，但存货占款29.11亿元，应付项目贡献32.51亿元，需拆分营运资本影响。
- 马钢有限和山钢日照合计账面价值约197.47亿元，上半年权益法收益合计仅约0.70亿元；低回报整合投资是估值折价的重要原因。
- 2025年每股分红0.30元，按参考价对应历史股息率约5.2%；2024—2026年每股分红承诺下限为0.20元。
- 60% P/B加40%正常化归母P/E估值的Bear/Base/Bull为3.59/6.21/9.55元，Base较参考价高8.0%。

模型包含8个工作表，14项勾稽全部为OK，公式错误扫描为零，所有工作表均已渲染并视觉验收。

## 本次会话此前成果：威高股份

### 文件

- [公司档案](companies/weigao-group/company-profile.md)
- [基本面研究报告](companies/weigao-group/research-report.md)
- [财务模型](companies/weigao-group/financial-model.xlsx)
- [来源索引](companies/weigao-group/source-index.md)
- [更新记录](companies/weigao-group/update-log.md)

### 研究结论

- 价格基准为2026-09-07收盘3.23港元；当前判断为谨慎积极，业务质量中上、盈利可见度中低、估值置信度中低。
- 2026H1收入68.49亿元、归母净利润7.74亿元，分别同比增长3.1%和下降23.2%；调整归母利润8.90亿元、同比下降11.7%。
- 毛利率下降3.43个百分点至46.3%，但经营现金流增长22.2%至10.78亿元；保守净现金39.26亿元。
- 贸易应收66.93亿元，其中一年以上9.45亿元；2025年末对同系附属公司的应收占贸易应收55.2%，需要持续核查回款与保理。
- 威高普瑞交易已获监管批准但尚未完成实施；并表会放大收入和利润，同时少数股东权益增加，必须看归母利润与现金分红而非合并规模。
- 正常化归母P/E加折价净现金估值的Bear/Base/Bull为2.40/4.89/7.55港元，Base较参考价高51.4%。

模型包含9个工作表，勾稽和公式错误扫描均通过，所有工作表均已渲染并视觉验收。

## 本次会话此前成果：梦百合

### 文件

- [公司档案](companies/mlily/company-profile.md)
- [基本面研究报告](companies/mlily/research-report.md)
- [财务模型](companies/mlily/financial-model.xlsx)
- [来源索引](companies/mlily/source-index.md)
- [更新记录](companies/mlily/update-log.md)

### 研究结论

- 价格基准为2026-09-04收盘6.43元；当前判断为中性偏谨慎，业务质量中等、盈利可见度低、估值置信度低。
- 2026H1收入46.55亿元、归母净利润0.05亿元、经营现金流5.45亿元、简化自由现金流3.62亿元；汇兑由上年同期收益转为损失，形成约1.22亿元同比反向波动。
- 境外线上收入13.74亿元、同比增长38.68%，但毛利率下降9.72个百分点至36.23%；销售费用率升至26.83%。
- 2025年财报因MC与Dormeo大额逾期应收被出具保留意见；2026H1相关应收原值约6.23亿元，仍有约3.12亿元逾期，实控人承诺在2026年末前代偿。
- 估值采用60%正常化P/E+40%P/B，Bear/Base/Bull为1.98/5.39/9.83元，Base较参考价低16.2%。

模型包含8个工作表，13项勾稽全部为OK，公式错误扫描为零，所有工作表均已渲染并视觉验收。

## 本次会话此前成果：信维通信

### 文件

- [公司档案](companies/sunway-communication/company-profile.md)
- [基本面研究报告](companies/sunway-communication/research-report.md)
- [财务模型](companies/sunway-communication/financial-model.xlsx)
- [来源索引](companies/sunway-communication/source-index.md)
- [更新记录](companies/sunway-communication/update-log.md)

### 研究结论

- 价格基准为2026-09-04收盘56.18元；约对应81.3倍滚动扣非P/E，判断为中性偏谨慎。
- 2026H1收入40.32亿元、扣非净利润1.41亿元，分别同比增长8.88%和22.05%；经营现金流4.40亿元，扣除5.75亿元资本开支后简化自由现金流-1.35亿元。
- 定增募资上限60亿元，三个项目总投资75.86亿元，已获证监会注册但尚未发行；Base按约13%摊薄建模。
- 拟以11亿元现金收购益阳信维电子55%股权；目标公司2025年亏损1.83亿元、2026H1亏损0.92亿元，交易待股东会审议。
- 2028E扣非P/E情景价值为15.18/43.64/81.63元，Base较参考价低22.3%。

模型包含10个工作表，公式错误扫描为零，检查表全部为OK，所有工作表均已渲染并视觉验收。

## 上次会话成果：达势股份

### 文件

- [公司档案](companies/dpc-dash/company-profile.md)
- [基本面研究报告](companies/dpc-dash/research-report.md)
- [财务模型](companies/dpc-dash/financial-model.xlsx)
- [来源索引](companies/dpc-dash/source-index.md)
- [更新记录](companies/dpc-dash/update-log.md)
- 原始披露位于 `companies/dpc-dash/source-documents/`

### 研究结论

- 价格基准：2026-09-04 收盘 30.50 港元；当前判断为中性偏积极，业务质量中高、盈利可见度中低、估值置信度中低。
- 2026H1 收入 31.34 亿元，同比增长 20.8%；交易量增长 33.7%，但 ATP 下降 9.6%、SSSG 为 -4.8%，门店经营利润率降至 12.5%。
- 第三方平台配送收入同比增长 81.0%、占收入 39.4%，自有渠道配送收入下降 11.8%；平台依赖和低价补贴是主要增长质量风险。
- 经营现金流 5.05 亿元，扣资本开支和租赁本金后的研究口径自由现金流约 -0.13 亿元；租赁调整净负债约 12.96 亿元。
- 估值采用 70% 2027E 调整 P/E + 30%租赁调整 EV/EBITDA；Bear/Base/Bull 为 17.19/40.67/67.57 港元，Base 较现价高 33.3%。
- 总特许经营协议当前期限至 2027-06-01，正式续约是最重要的催化剂与风险；2026-08-31 新授期权和股份奖励合计约当时股本 3.37%，模型采用摊薄股本。

模型包含 Cover、Historical、Unit Economics、Balance & Cash、Assumptions、Forecast、Valuation、Checks、Sources Audit 共 9 个工作表；公式错误扫描为零，检查表全部为 OK，所有工作表均已渲染并视觉验收。

## 最近成果：保利物业和中海物业

### 文件

- 保利物业：[公司档案](companies/poly-property-services/company-profile.md)、[研究报告](companies/poly-property-services/research-report.md)、[来源索引](companies/poly-property-services/source-index.md)、[更新记录](companies/poly-property-services/update-log.md)、[财务模型](companies/poly-property-services/financial-model.xlsx)
- 中海物业：[公司档案](companies/china-overseas-property/company-profile.md)、[研究报告](companies/china-overseas-property/research-report.md)、[来源索引](companies/china-overseas-property/source-index.md)、[更新记录](companies/china-overseas-property/update-log.md)、[财务模型](companies/china-overseas-property/financial-model.xlsx)

### 对比结论

- 保利物业 2026H1 收入 88.29 亿元、归母净利润 9.33 亿元，基础物管收入增长 11.9%；但应收款较年初增长约 28.7%，两类增值服务均双位数下滑。研究口径净现金 122.48 亿元，Base 价值 36.73 港元，较 28.76 港元高 27.7%，判断为谨慎积极。
- 中海物业 2026H1 收入 74.85 亿元、归母净利润 7.01 亿元，毛利率降至 14.9%、经营现金流转为 -5.02 亿元，应收款较年初增长 38.4%。新签面积 85.9%来自第三方，并主动退出 1,920 万平方米亏损或到期项目。Base 价值 4.33 港元，较 3.575 港元高 21.2%，判断为中性观察。
- 保利物业采用正常化 P/E 加折价可分配现金；中海物业采用 70% 正常化 P/E 加 30% 股息资本化。两家公司估值都不能脱离现金回款和关联财务安排单独理解。

两套模型均包含 Cover、Historical、Operations、Balance & Cash、Assumptions、Forecast、Valuation、Checks、Sources Audit 共 9 个工作表；公式错误扫描为零，检查表全部为 OK，所有工作表均已渲染并视觉验收。

## 最近成果：天齐锂业、赣锋锂业和云铝股份

### 文件

- 天齐锂业：[公司档案](companies/tianqi-lithium/company-profile.md)、[研究报告](companies/tianqi-lithium/research-report.md)、[来源索引](companies/tianqi-lithium/source-index.md)、[更新记录](companies/tianqi-lithium/update-log.md)、[财务模型](companies/tianqi-lithium/financial-model.xlsx)
- 赣锋锂业：[公司档案](companies/ganfeng-lithium/company-profile.md)、[研究报告](companies/ganfeng-lithium/research-report.md)、[来源索引](companies/ganfeng-lithium/source-index.md)、[更新记录](companies/ganfeng-lithium/update-log.md)、[财务模型](companies/ganfeng-lithium/financial-model.xlsx)
- 云铝股份：[公司档案](companies/yunnan-aluminum/company-profile.md)、[研究报告](companies/yunnan-aluminum/research-report.md)、[来源索引](companies/yunnan-aluminum/source-index.md)、[更新记录](companies/yunnan-aluminum/update-log.md)、[财务模型](companies/yunnan-aluminum/financial-model.xlsx)

### 对比结论

- 天齐锂业的核心质量来自 Greenbushes 与 SQM，但 2026H1 约 42.42 亿元归母利润含约 14.07 亿元 SQM 权益法收益；基准价值 48.97 元，较 45.35 元现价仅高 8.0%，判断为中性观察。
- 赣锋锂业拥有更广的资源与项目组合，但 2026H1 经营现金流约 13.28 亿元、资本开支约 24.35 亿元，研究口径净债务约 257.37 亿元；基准价值 45.27 元，低于 50.52 元现价 10.4%，判断为中性偏谨慎。
- 云铝股份 2026H1 约 76.84 亿元归母利润对应约 83.77 亿元经营现金流，研究口径净现金约 154.95 亿元，利润质量最佳；但基准价值 24.10 元低于 26.95 元现价 10.6%，判断为中性观察。
- 三家公司均采用正常化盈利，未把 2026H1 高景气利润直接年化。锂企模型为 60% P/E + 40% P/B，云铝为 70% P/E + 30% P/B。

三套模型均包含 Cover、Historical、Operations、Balance & Cash、Assumptions、Valuation、Checks、Sources Audit 共 8 个工作表；公式错误扫描为零，检查表全部为 OK，所有工作表均已渲染并视觉验收。

## 最近成果：牧原股份

### 文件

- [公司档案](companies/muyuan/company-profile.md)
- [基本面研究报告](companies/muyuan/research-report.md)
- [财务模型](companies/muyuan/financial-model.xlsx)
- [来源索引](companies/muyuan/source-index.md)
- [更新记录](companies/muyuan/update-log.md)
- 原始披露位于 `companies/muyuan/source-documents/`

### 研究结论

- 价格基准：2026-09-04 A 股收盘 43.97 元。
- 当前判断：中性观察；业务质量中高、盈利可见度低、估值置信度中低。
- 2026H1 收入 594.10 亿元、归母亏损 60.78 亿元、经营现金流 -22.24 亿元、简化自由现金流 -87.45 亿元。
- 商品猪均价约 10.4 元/kg；6 月完全成本约 11.7 元/kg。7 月商品猪均价 10.64 元/kg、完全成本约 11.5 元/kg，单位价差仍为负。
- 2026H1 商品猪销量 3,861.5 万头、屠宰量 1,723.4 万头；屠宰量同比约 +51%，上半年每月均盈利，但分部毛利率仅 4.2%。
- 广义净债务约 572.50 亿元，流动比率约 0.79；H 股融资提供缓冲，但周期底部的短债和现金流压力仍高。
- 估值采用 60% 正常化 P/E + 40% P/B。

| 情景 | 2027 商品猪均价 | 完全成本 | 归母净利润 | P/E | P/B | 每股价值 | 相对 43.97 元 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bear | 12.50 元/kg | 11.80 元/kg | 85.47 亿元 | 9x | 1.8x | 18.22 元 | -58.6% |
| Base | 13.50 元/kg | 11.20 元/kg | 249.25 亿元 | 13x | 2.6x | 48.71 元 | +10.8% |
| Bull | 14.50 元/kg | 10.90 元/kg | 393.79 亿元 | 15x | 3.4x | 81.26 元 | +84.8% |

最重要的反方是：生产效率提升可能抵消母猪去化，使猪价长期停留在低位；即使牧原保持成本领先，也可能只体现为份额提升而非高资本回报。后续主要跟踪商品猪价格、完全成本、经营现金流、广义净债务和屠宰单位利润。

财务模型包含 8 个工作表：Cover、Historical、Operations、Balance & Cash、Assumptions、Valuation、Checks、Sources Audit；Cover 有单位售价/成本和情景价值两张图。模型公式错误扫描为零，检查表全部为 OK，所有工作表已渲染并视觉验收。

## 研究和更新标准

### 来源优先级

1. 交易所公告、经审计年报、公司正式财报和经营数据公告。
2. 公司正式业绩材料、投资者关系记录和监管问询回复。
3. 行业协会、政府统计、权威行业数据库。
4. 市场价格接口和可靠二级来源；必须注明日期。
5. 新闻、券商和媒体只用于补充线索，不能替代关键财务事实。

### 财务与估值

- 优先重构收入、利润、扣非利润、经营现金流、资本开支、自由现金流、股本和净债务。
- 对一次性损益、资产公允价值、政府补助、处置收益、研发资本化和会计口径变化单独处理。
- 周期公司使用正常化盈利，不把高景气半年或单季直接年化。
- 估值框架按行业选择 P/E、P/B、EV/EBITDA、DCF、SOTP 或 rNPV，避免所有公司使用同一倍数。
- 每个关键模型输入应能追溯到来源或被明确标记为分析假设。

### 模型和文件验收

- 财务模型需保留输入、公式、来源、检查和关键图表。
- 至少检查关键范围、Bear/Base/Bull 公式、股本桥、净债务桥和错误单元格。
- 所有工作表均需渲染并目视检查文字截断、图表位置、比例和颜色。
- 最终模型复制到公司档案目录；生成与验收产物保留在 `outputs/<research-run>/`。
- 验证 Markdown 本地链接和总览公司数量。

## 新会话建议启动方式

如果新会话仍在 `D:\Research` 项目中，可直接提出任务，例如：

> 使用 Equity Research 更新宝丰能源最新季报。先读取项目 AGENTS.md、PROJECT_CONTEXT.md、stock-overview.md 和宝丰能源现有档案；使用最新正式披露更新来源、模型、报告、总览和本项目上下文。

如果怀疑项目说明没有自动加载，可要求：

> 请先说明你读取到的 AGENTS.md 和 PROJECT_CONTEXT.md，再开始工作。

## 当前未完成事项

截至 2026-09-07，达势股份建档及全库总览更新没有遗留的必做事项。下一次工作应由新的公司分析、财报发布、估值假设变化或用户指定的研究问题触发。

## 维护本文件

- 新增公司、重大财报更新、估值方法改变、项目路径变化或研究规则变化后，更新“最后更新”“当前覆盖”“已完成工作”和相关公司摘要。
- 不需要逐字保存聊天；只保存以后会影响判断、文件位置、工作流程和结果复核的持久信息。
- 如果本文件与公司最新报告冲突，以最新正式披露和更新后的公司报告为准，并同步修订本文件。
