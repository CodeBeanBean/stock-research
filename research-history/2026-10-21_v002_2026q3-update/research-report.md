# 2026年三季报全库核查与更新汇总

**研究/核查日：2026-10-21上午。** 覆盖37家：23家有A股上市、14家仅港股；A/H同一发行人计一次。固定价格为10月20日已收盘，未使用21日行情。公告检索期10月15日至21日，具体采集UTC在逐家公司JSON；与15日晚永久核查衔接，不把检索完成后的新公告提前视作已知。

## 本轮完成了什么

- **宁德时代：新增完整Q3**，模型、分析、股本、价格和三情景估值均更新。
- **天齐锂业：新增前三季业绩预告**，更新利润区间和准则/股本，明确不是完整Q3；未推算尚未披露的现金与资产负债。
- **赣锋：已有完整Q3及环比专项分析**，本轮公告与已处理原件相同，未重复生成新估值。
- 其余34家公司在检索范围内未发现新完整Q3；回购、担保、经营月报、部分要约等不充作财务三季报。未统一刷新其价格和旧估值。

## 研究结论与估值变化

| 公司 | 最新财报性质 | 旧Base→新Base | 10月20日A股价 | 新Bear/Base/Bull | 判断 | 实质变化 |
|---|---|---:|---:|---|---|---|
| [宁德时代](../../companies/catl/research-history/2026-10-21_v002_2026q3-update/research-report.md) | 完整Q3，未经审计 | 493.21→384.33元 | 259.08元 | 185.42/384.33/683.34元 | 中性偏积极 | 毛利和现金转弱，下调净利率及倍数，全发行股本 |
| [天齐锂业](../../companies/tianqi-lithium/research-history/2026-10-21_v002_2026q3-guidance/research-report.md) | 前三季预告，未预审计 | 48.97→48.66元 | 36.50元 | 22.99/48.66/75.62元 | 中性观察 | 预告隐含Q3放缓，保留正常化盈利，统一CAS资产锚 |

### 宁德：增长还在，利润和现金质量降温

Q3收入1652.21亿元、归母212.46亿元、扣非188.62亿元，环比分别+11.8%、-5.8%、-9.8%；毛利率20.69%，较Q2下降2.47个百分点。Q3经营现金仅14.09亿元、购建长期资产170.95亿元，简化现金缺口156.86亿元。应收和存货增加、应付账款下降与资金占用方向相符，但无季度调节明细，不能编造完整现金归因。
[正式Q3报告](../../companies/catl/source-documents/Q301-2026-10-21-quarterly.pdf)

2027 Base收入7200亿元保留，净利率15%降至13%、P/E21降至19；股本改用46.2725亿全发行股份，未提前扣未来注销。Base下修22.1%，而价格较旧337.11元下降23.1%，故空间仍为48.3%。这是价格下降抵消估值下调，不能说因财报超预期而上调。H股同日411.80港元，按汇率Base空间仅9.7%，不套用A股空间。

### 天齐：累计同比高增掩盖环比放缓

前三季预告归母51–60亿元；减CAS H1的42.42亿元，Q3隐含8.58–17.58亿元，较Q2下降25.7%–63.7%。扣非隐含8.30–17.30亿元、较Q2下降27.4%–65.2%。SQM尚未披露Q3，公司按测算模型及彭博预测估计权益法收益，不是已收现金股息。
[正式业绩预告](../../companies/tianqi-lithium/source-documents/Q301-2026-10-21-guidance.pdf)

不据同比高增上调正常化EPS和倍数；只将P/B净资产由IFRS491.68亿元改为同日CAS483.43亿元，股数按9月月报修订。新Base48.66元、空间33.3%，主要因为价格45.35降至36.50元。正式Q3现金、债务和权益尚未知。

## 逐家公司结果与可复核查询

“未检出”是本轮检索时点与范围内的状态，不能推断公司以后不发布季度报告。港股很多公司不发布完整Q3，不用月度营运或其他公告替代。

| 公司 | 代码 | 完整Q3状态 | 本轮处理 | 官方查询原始结果 |
|---|---|---|---|---|
| [歌华有线](../../companies/gehua-cable/research-report.md) | 600037.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/gehua-cable-cninfo-page1.json) |
| [赛轮轮胎](../../companies/sailun/research-report.md) | 601058.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/sailun-cninfo-page1.json) |
| [蜜雪集团](../../companies/mixue/research-report.md) | 02097.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/mixue-hkex.json) |
| [分众传媒](../../companies/focus-media/research-report.md) | 002027.SZ | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/focus-media-cninfo-page1.json) |
| [朗姿股份](../../companies/lancy/research-report.md) | 002612.SZ | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/lancy-cninfo-page1.json) |
| [春秋航空](../../companies/spring-airlines/research-report.md) | 601021.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/spring-airlines-cninfo-page1.json) |
| [美的集团](../../companies/midea-group/research-report.md) | 000333.SZ / 00300.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/midea-group-cninfo-page1.json) |
| [宁德时代](../../companies/catl/research-history/2026-10-21_v002_2026q3-update/research-report.md) | 300750.SZ / 03750.HK | 新发布，已更新 | 9表财务模型、季度与现金、估值下修 | [查询](evidence/catl-cninfo-page1.json) |
| [思格新能](../../companies/sigenergy/research-report.md) | 06656.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/sigenergy-hkex.json) |
| [龙湖集团](../../companies/longfor-group/research-report.md) | 00960.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/longfor-group-hkex.json) |
| [万华化学](../../companies/wanhua-chemical/research-report.md) | 600309.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/wanhua-chemical-cninfo-page1.json) |
| [伊利股份](../../companies/yili/research-report.md) | 600887.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/yili-cninfo-page1.json) |
| [恒隆地产](../../companies/hang-lung-properties/research-report.md) | 00101.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/hang-lung-properties-hkex.json) |
| [珀莱雅](../../companies/proya/research-report.md) | 603605.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/proya-cninfo-page1.json) |
| [宝钢股份](../../companies/baosteel/research-report.md) | 600019.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/baosteel-cninfo-page1.json) |
| [威高股份](../../companies/weigao-group/research-report.md) | 01066.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/weigao-group-hkex.json) |
| [梦百合](../../companies/mlily/research-report.md) | 603313.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/mlily-cninfo-page1.json) |
| [福寿园](../../companies/fu-shou-yuan/research-report.md) | 01448.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/fu-shou-yuan-hkex.json) |
| [信维通信](../../companies/sunway-communication/research-report.md) | 300136.SZ | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/sunway-communication-cninfo-page1.json) |
| [达势股份](../../companies/dpc-dash/research-report.md) | 01405.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/dpc-dash-hkex.json) |
| [保利物业](../../companies/poly-property-services/research-report.md) | 06049.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/poly-property-services-hkex.json) |
| [中海物业](../../companies/china-overseas-property/research-report.md) | 02669.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/china-overseas-property-hkex.json) |
| [天齐锂业](../../companies/tianqi-lithium/research-history/2026-10-21_v002_2026q3-guidance/research-report.md) | 002466.SZ / 09696.HK | 完整Q3未检出；有业绩预告 | 已分析预告，正式财报待发布 | [查询](evidence/tianqi-lithium-cninfo-page1.json) |
| [赣锋锂业](../../companies/ganfeng-lithium/research-report.md) | 002460.SZ / 01772.HK | 已发布，库内已更新 | 沿用10月15日估值及16日专项，不刷新价格 | [查询](evidence/ganfeng-lithium-cninfo-page1.json) |
| [云铝股份](../../companies/yunnan-aluminum/research-report.md) | 000807.SZ | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/yunnan-aluminum-cninfo-page1.json) |
| [牧原股份](../../companies/muyuan/research-report.md) | 002714.SZ / 02714.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/muyuan-cninfo-page1.json) |
| [宝丰能源](../../companies/baofeng-energy/research-report.md) | 600989.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/baofeng-energy-cninfo-page1.json) |
| [兆易创新](../../companies/gigadevice/research-report.md) | 603986.SH / 03986.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/gigadevice-cninfo-page1.json) |
| [阳光电源](../../companies/sungrow/research-report.md) | 300274.SZ | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/sungrow-cninfo-page1.json) |
| [晋亿实业](../../companies/jinyi-industrial/research-report.md) | 601002.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/jinyi-industrial-cninfo-page1.json) |
| [百联股份](../../companies/bailian/research-report.md) | 600827.SH | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/bailian-cninfo-page1.json) |
| [宋城演艺](../../companies/songcheng-performance/research-report.md) | 300144.SZ | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/songcheng-performance-cninfo-page1.json) |
| [腾讯控股](../../companies/tencent/research-report.md) | 0700.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/tencent-hkex.json) |
| [三生制药](../../companies/3sbio/research-report.md) | 01530.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/3sbio-hkex.json) |
| [海吉亚医疗](../../companies/hygeia-healthcare/research-report.md) | 06078.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/hygeia-healthcare-hkex.json) |
| [海底捞](../../companies/haidilao/research-report.md) | 06862.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/haidilao-hkex.json) |
| [中国民航信息网络](../../companies/travelsky/research-report.md) | 00696.HK | 未检出新完整Q3 | 保持公司原价格和估值日期 | [查询](evidence/travelsky-hkex.json) |

## 核查边界及后续事项

其他公告已保留在原始查询结果，本轮不扩展为37家公司所有非财报事项全面重估。前次达势/龙湖/春秋经营及福寿园复牌分析仍是[历史核查记录](../2026-10-15_v001_2026q3-disclosure-check/research-report.md)，不能当作本次重新验证的全部事实。

优先等待宁德现金回收及资本开支、动力/储能分部毛利和售后义务；天齐正式Q3及SQM最终业绩、实际股利和净债务。未创建自动监控。其余公司后续季报须以实际刊发为准。

两家公司当前报告和模型对应永久版本，留档包含关键事实、假设、价格及估值变化，见[宁德历史](../../companies/catl/research-history/index.md)、[天齐历史](../../companies/tianqi-lithium/research-history/index.md)、[全库历史](../index.md)。
