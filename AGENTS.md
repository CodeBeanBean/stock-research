# Stock Research 项目规则

## 项目定位

这是一个长期维护的上市公司基本面研究库。每次任务应增量更新已有档案，避免在新位置重复建库。

## 必读文件

- 项目长期上下文：`PROJECT_CONTEXT.md`
- 全库估值与导航：`stock-overview.md`
- 项目结构说明：`README.md`
- 已覆盖公司的现有档案：`companies/<company>/`

## 标准工作流

- 公司基本面分析和财报更新使用 `equity-research` skill。
- 创建或修改 `.xlsx` 财务模型时同时使用 `spreadsheets` skill，并完成公式检查、关键范围检查、全部工作表渲染和视觉验收。
- 财务事实优先使用交易所公告、经审计年报、公司正式财报和经营公告；市场价格注明日期、币种及来源。
- 明确区分原始披露、研究计算、管理层口径和分析假设；不把一次性损益或周期峰值机械年化。
- 估值至少包含 Bear、Base、Bull，写明关键假设、最强反方、催化剂、风险和证伪条件。
- 新建公司或进行重大财报/估值更新后，同步更新 `stock-overview.md`、`README.md`、公司 `update-log.md` 和本文件指向的 `PROJECT_CONTEXT.md` 状态部分。
- 每家公司通常保留：`company-profile.md`、`research-report.md`、`financial-model.xlsx`、`source-index.md`、`update-log.md`、`source-documents/`。
- 财务模型 Cover 必须有有用的核心图表；不得只生成文字封面。
- 交付前验证本地链接、覆盖公司数量、估值公式、错误单元格和文件路径。

## 文件与目录约束

- 正式档案只写入 `D:\Research\stock-research`。
- `companies/<company>/` 是公司档案的唯一正式位置。
- `outputs/<research-run>/` 保存每次模型生成及验收产物；`.work/` 只用于可复现脚本和临时依赖。
- 报告和模型是公司估值的源数据；`stock-overview.md` 只是快照和导航层。

## 时效性

- `PROJECT_CONTEXT.md` 和 `stock-overview.md` 不是实时行情或最新财报数据库。
- 只要用户提出“最新”“已出财报”“更新”等请求，就必须重新核对当前日期下的正式披露和市场价格。
- 历史估值结论不得在未更新价格、股本和财报的情况下直接复用为当前结论。

