# Yahoo Finance API 接口文档

本文档描述了 `fast-finance` 的 Yahoo Finance 数据接口。
所有数据直接来源于 Yahoo Finance，响应字段已统一转换为 **小驼峰 (camelCase)** 格式。
以下参数列表基于实际 API 调用生成，包含尽可能完整的字段。

---

## 1. 股票详情 (Info)

**URL**: `/api/v1/yahoo/info` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |

### 响应参数

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| 52weekchange | float | 52周涨跌幅 |
| address1 | str | 地址 |
| alltimehigh | float | 历史最高价 |
| alltimelow | float | 历史最低价 |
| ask | float | 卖一价 |
| asksize | int | 卖一量 |
| auditrisk | int | 审计风险评分 |
| averageanalystrating | str | 平均分析师评级 |
| averagedailyvolume10day | int | 10日日均成交量 |
| averagedailyvolume3month | int | 3个月日均成交量 |
| averagevolume | int | 平均成交量 (3个月) |
| averagevolume10days | int | 平均成交量 (10日) |
| beta | float | Beta系数 |
| bid | float | 买一价 |
| bidsize | int | 买一量 |
| boardrisk | int | 董事会风险评分 |
| bookvalue | float | 每股净资产 |
| city | str | 城市 |
| companyofficers | list | 高管列表 |
| compensationasofepochdate | int | 薪酬数据基准日 |
| compensationrisk | int | 薪酬风险评分 |
| corporateactions | list | 公司行动 (派息/拆股) |
| country | str | 国家 |
| cryptotradeable | bool | 是否支持加密交易 |
| currency | str | 货币 |
| currentprice | float | 当前价格 |
| currentratio | float | 流动比率 |
| custompricealertconfidence | str | 价格预警置信度 |
| dateshortinterest | int | 做空数据统计日 |
| dayhigh | float | 今日最高价 |
| daylow | float | 今日最低价 |
| debttoequity | float | 产权比率 |
| displayname | str | 显示名称 |
| dividenddate | int | 派息日 |
| dividendrate | float | 股息金额 |
| dividendyield | float | 股息率 |
| earningscalltimestampend | int | 电话会议结束时间 |
| earningscalltimestampstart | int | 电话会议开始时间 |
| earningsgrowth | float | 盈利增长率 |
| earningsquarterlygrowth | float | 季度盈利增长率 |
| earningstimestamp | int | 财报发布时间 |
| earningstimestampend | int | 财报预计结束时间 |
| earningstimestampstart | int | 财报预计开始时间 |
| ebitda | int | 息税折旧摊销前利润 (EBITDA) |
| ebitdamargins | float | EBITDA率 |
| enterprisetoebitda | float | EV/EBITDA比 |
| enterprisetorevenue | float | EV/营收比 (EV/Revenue) |
| enterprisevalue | int | 企业价值 (EV) |
| epscurrentyear | float | 本年EPS预估 |
| epsforward | float | 远期EPS (Forward EPS) |
| epstrailingtwelvemonths | float | 滚动EPS (TTM) |
| esgpopulated | bool | ESG数据是否已填充 |
| exchange | str | 交易所 |
| exchangedatadelayedby | int | 行情延迟 (分钟) |
| exchangetimezonename | str | 交易所所在时区名 |
| exchangetimezoneshortname | str | 交易所时区简称 |
| exdividenddate | int | 除息日 |
| executiveteam | list | 核心管理团队 |
| fiftydayaverage | float | 50日均线 (MA50) |
| fiftydayaveragechange | float | 当前价距MA50变动额 |
| fiftydayaveragechangepercent | float | 当前价距MA50变动率 |
| fiftytwoweekchangepercent | float | 52周涨跌幅 |
| fiftytwoweekhigh | float | 52周最高价 |
| fiftytwoweekhighchange | float | 距52周最高价变动额 |
| fiftytwoweekhighchangepercent | float | 距52周最高价变动率 |
| fiftytwoweeklow | float | 52周最低价 |
| fiftytwoweeklowchange | float | 距52周最低价变动额 |
| fiftytwoweeklowchangepercent | float | 距52周最低价变动率 |
| fiftytwoweekrange | str | 52周价格区间 |
| financialcurrency | str | 财报货币 |
| firsttradedatemilliseconds | int | 首次交易时间戳 |
| fiveyearavgdividendyield | float | 5年平均股息率 |
| floatshares | int | 流通股 |
| forwardeps | float | 远期每股收益预测 |
| forwardpe | float | 远期市盈率 |
| freecashflow | int | 自由现金流 |
| fullexchangename | str | 交易所全称 |
| fulltimeemployees | int | 全职员工 |
| gmtoffsetmilliseconds | int | GMT偏移量 (毫秒) |
| governanceepochdate | int | 治理评分基准日 |
| grossmargins | float | 毛利率 |
| grossprofits | int | 毛利 |
| hasprepostmarketdata | bool | 是否有盘前盘后数据 |
| heldpercentinsiders | float | 内部持股比例 |
| heldpercentinstitutions | float | 机构持股比例 |
| impliedsharesoutstanding | int | 隐含稀释总股本 |
| industry | str | 行业 |
| industrydisp | str | 行业展示名 |
| industrykey | str | 行业Key |
| irwebsite | str | 投资者关系主页 |
| isearningsdateestimate | bool | 财报日期是否为预估 |
| language | str | 语言 |
| lastdividenddate | int | 最近一次派息日 |
| lastdividendvalue | float | 最近一次派息金额 |
| lastfiscalyearend | int | 上一财年结束日 |
| lastsplitdate | int | 最近拆股日期 |
| lastsplitfactor | str | 最近拆股比例 |
| longbusinesssummary | str | 业务描述 |
| longname | str | 公司全称 |
| market | str | 市场 |
| marketcap | int | 市值 |
| marketstate | str | 市场状态 (REGULAR/CLOSED) |
| maxage | int | 数据最大缓存时间 |
| messageboardid | str | 论坛板块ID |
| mostrecentquarter | int | 最近财季结束日 |
| netincometocommon | int | 归母净利润 |
| nextfiscalyearend | int | 下一财年结束日 |
| numberofanalystopinions | int | 分析师数量 |
| open | float | 开盘价 |
| operatingcashflow | int | 经营现金流 |
| operatingmargins | float | 营业利润率 |
| overallrisk | int | 整体风险评分 |
| payoutratio | float | 派息比率 |
| phone | str | 电话 |
| previousclose | float | 前一日收盘价 |
| priceepscurrentyear | float | 本年预期市盈率 |
| pricehint | int | 价格精度提示 |
| pricetobook | float | 市净率 (PB) |
| pricetosalestrailing12months | float | 市销率 (PS TTM) |
| profitmargins | float | 净利率 |
| quickratio | float | 速动比率 |
| quotesourcename | str | 报价数据源 |
| quotetype | str | 证券类型 |
| recommendationkey | str | 综合评级 |
| recommendationmean | int | 平均评级 |
| region | str | 地区 |
| regularmarketchange | float | 常规交易涨跌额 |
| regularmarketchangepercent | float | 常规交易涨跌幅 |
| regularmarketdayhigh | float | 常规交易日最高 |
| regularmarketdaylow | float | 常规交易日最低 |
| regularmarketdayrange | str | 常规交易日价格区间 |
| regularmarketopen | float | 常规交易开盘价 |
| regularmarketpreviousclose | float | 常规交易昨收 |
| regularmarketprice | float | 常规交易时段价格 |
| regularmarkettime | int | 常规交易时间戳 |
| regularmarketvolume | int | 常规交易成交量 |
| returnonassets | float | 总资产回报率 (ROA) |
| returnonequity | float | 净资产收益率 (ROE) |
| revenuegrowth | float | 营收增长率 |
| revenuepershare | float | 每股营收 |
| sandp52weekchange | float | 标普500同期涨跌幅 |
| sector | str | 板块 |
| sectordisp | str | 板块展示名 |
| sectorkey | str | 板块Key |
| shareholderrightsrisk | int | 股东权益风险评分 |
| sharesoutstanding | int | 总股本 |
| sharespercentsharesout | float | 做空占总股本比例 |
| sharesshort | int | 做空股数 |
| sharesshortpreviousmonthdate | int | 上月做空数据统计日 |
| sharesshortpriormonth | int | 上月做空股数 |
| shortname | str | 公司简称 |
| shortpercentoffloat | float | 做空占流通股比例 |
| shortratio | float | 做空比率 |
| sourceinterval | int | 数据源间隔 |
| state | str | 州/省 |
| symbol | str | 股票代码 |
| targethighprice | int | 目标最高价 |
| targetlowprice | int | 目标最低价 |
| targetmeanprice | float | 目标平均价 |
| targetmedianprice | int | 目标中位价 |
| totalcash | int | 总现金 |
| totalcashpershare | float | 每股现金 |
| totaldebt | int | 总债务 |
| totalrevenue | int | 总营收 |
| tradeable | bool | 是否可交易 |
| trailingannualdividendrate | float | 滚动年度股息金额 |
| trailingannualdividendyield | float | 滚动年度股息率 |
| trailingeps | float | 滚动每股收益 (EPS TTM) |
| trailingpe | float | 滚动市盈率 |
| trailingpegratio | float | 滚动PEG比率 |
| triggerable | bool | 是否可触发通知 |
| twohundreddayaverage | float | 200日均线 (MA200) |
| twohundreddayaveragechange | float | 当前价距MA200变动额 |
| twohundreddayaveragechangepercent | float | 当前价距MA200变动率 |
| typedisp | str | 展示类型 |
| volume | int | 成交量 |
| website | str | 官网 |
| zip | str | 邮编 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": {
    "address1": "One Apple Park Way",
    "city": "Cupertino",
    "state": "CA",
    "zip": "95014",
    "country": "United States",
    "phone": "(408) 996-1010",
    "website": "https://www.apple.com",
    "industry": "Consumer Electronics",
    "industrykey": "consumer-electronics",
    "industrydisp": "Consumer Electronics",
    "sector": "Technology",
    "sectorkey": "technology",
    "sectordisp": "Technology",
    "longbusinesssummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide...",
    "fulltimeemployees": 166000,
    "companyofficers": [
      {
        "name": "Mr. Timothy D. Cook",
        "title": "CEO & Director",
        "totalpay": 16520856
      }
    ],
    "auditrisk": 7,
    "boardrisk": 1,
    "compensationrisk": 3,
    "shareholderrightsrisk": 1,
    "overallrisk": 1,
    "governanceepochdate": 1764547200,
    "compensationasofepochdate": 1735603200,
    "irwebsite": "http://investor.apple.com/",
    "executiveteam": [],
    "maxage": 86400,
    "pricehint": 2,
    "previousclose": 274.11,
    "open": 272.82,
    "daylow": 271.79,
    "dayhigh": 273.93,
    "regularmarketpreviousclose": 274.11,
    "regularmarketopen": 272.82,
    "regularmarketdaylow": 271.79,
    "regularmarketdayhigh": 273.93,
    "dividendrate": 1.04,
    "dividendyield": 0.38,
    "exdividenddate": 1762732800,
    "payoutratio": 0.1367,
    "fiveyearavgdividendyield": 0.53,
    "beta": 1.107,
    "trailingpe": 36.50067,
    "forwardpe": 29.877747,
    "volume": 3192454,
    "regularmarketvolume": 3192454,
    "averagevolume": 48856580,
    "averagevolume10days": 41495090,
    "averagedailyvolume10day": 41495090,
    "bid": 271.02,
    "ask": 272.88,
    "bidsize": 4,
    "asksize": 6,
    "marketcap": 4040964177920,
    "fiftytwoweeklow": 169.21,
    "fiftytwoweekhigh": 288.62,
    "alltimehigh": 288.62,
    "alltimelow": 0.049107,
    "pricetosalestrailing12months": 9.710098,
    "fiftydayaverage": 268.177,
    "twohundreddayaverage": 229.1754,
    "trailingannualdividendrate": 1.02,
    "trailingannualdividendyield": 0.003721134,
    "currency": "USD",
    "tradeable": false,
    "enterprisevalue": 4108026118144,
    "profitmargins": 0.26915002,
    "floatshares": 14750642146,
    "sharesoutstanding": 14776353000,
    "sharesshort": 129458559,
    "sharesshortpriormonth": 115557836,
    "sharesshortpreviousmonthdate": 1761868800,
    "dateshortinterest": 1764288000,
    "sharespercentsharesout": 0.0088,
    "heldpercentinsiders": 0.016970001,
    "heldpercentinstitutions": 0.64404,
    "shortratio": 2.64,
    "shortpercentoffloat": 0.0088,
    "impliedsharesoutstanding": 14840390000,
    "bookvalue": 4.991,
    "pricetobook": 54.557205,
    "lastfiscalyearend": 1758931200,
    "nextfiscalyearend": 1790467200,
    "mostrecentquarter": 1758931200,
    "earningsquarterlygrowth": 0.864,
    "netincometocommon": 112010002432,
    "trailingeps": 7.46,
    "forwardeps": 9.11364,
    "lastsplitfactor": "4:1",
    "lastsplitdate": 1598832000,
    "enterprisetorevenue": 9.871,
    "enterprisetoebitda": 28.381,
    "52weekchange": 0.08138704,
    "sandp52weekchange": 0.12658226,
    "lastdividendvalue": 0.26,
    "lastdividenddate": 1762732800,
    "quotetype": "EQUITY",
    "currentprice": 272.295,
    "targethighprice": 350,
    "targetlowprice": 215,
    "targetmeanprice": 286.57584,
    "targetmedianprice": 300,
    "recommendationmean": 2,
    "recommendationkey": "buy",
    "numberofanalystopinions": 41,
    "totalcash": 54697000960,
    "totalcashpershare": 3.702,
    "ebitda": 144748003328,
    "totaldebt": 112377004032,
    "quickratio": 0.771,
    "currentratio": 0.893,
    "totalrevenue": 416161005568,
    "debttoequity": 152.411,
    "revenuepershare": 27.84,
    "returnonassets": 0.22964,
    "returnonequity": 1.7142199,
    "grossprofits": 195201007616,
    "freecashflow": 78862254080,
    "operatingcashflow": 111482003456,
    "earningsgrowth": 0.912,
    "revenuegrowth": 0.079,
    "grossmargins": 0.46905,
    "ebitdamargins": 0.34782,
    "operatingmargins": 0.31647,
    "financialcurrency": "USD",
    "symbol": "AAPL",
    "language": "en-US",
    "region": "US",
    "typedisp": "Equity",
    "quotesourcename": "Nasdaq Real Time Price",
    "triggerable": true,
    "custompricealertconfidence": "HIGH",
    "gmtoffsetmilliseconds": -18000000,
    "esgpopulated": false,
    "regularmarketchangepercent": -0.66213274,
    "regularmarketprice": 272.295,
    "corporateactions": [],
    "regularmarkettime": 1765896232,
    "exchange": "NMS",
    "messageboardid": "finmb_24937",
    "exchangetimezonename": "America/New_York",
    "exchangetimezoneshortname": "EST",
    "market": "us_market",
    "marketstate": "REGULAR",
    "hasprepostmarketdata": true,
    "firsttradedatemilliseconds": 345479400000,
    "regularmarketchange": -1.8149719,
    "regularmarketdayrange": "271.79 - 273.93",
    "fullexchangename": "NasdaqGS",
    "averagedailyvolume3month": 48856580,
    "shortname": "Apple Inc.",
    "longname": "Apple Inc.",
    "cryptotradeable": false,
    "fiftytwoweeklowchange": 103.08501,
    "fiftytwoweeklowchangepercent": 0.6092134,
    "fiftytwoweekrange": "169.21 - 288.62",
    "fiftytwoweekhighchange": -16.324982,
    "fiftytwoweekhighchangepercent": -0.0565622,
    "fiftytwoweekchangepercent": 8.138704,
    "dividenddate": 1762992000,
    "earningstimestamp": 1761854400,
    "earningstimestampstart": 1769720400,
    "earningstimestampend": 1769720400,
    "earningscalltimestampstart": 1761858000,
    "earningscalltimestampend": 1761858000,
    "isearningsdateestimate": true,
    "epstrailingtwelvemonths": 7.46,
    "epsforward": 9.11364,
    "epscurrentyear": 8.22857,
    "priceepscurrentyear": 33.091415,
    "fiftydayaveragechange": 4.1180115,
    "fiftydayaveragechangepercent": 0.015355573,
    "twohundreddayaveragechange": 43.119614,
    "twohundreddayaveragechangepercent": 0.18815115,
    "sourceinterval": 15,
    "exchangedatadelayedby": 0,
    "averageanalystrating": "2.0 - Buy",
    "displayname": "Apple",
    "trailingpegratio": 2.7739
  }
}
```

---

## 2. 历史 K 线 (History)

**URL**: `/api/v1/yahoo/history` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |
| period | str (enum) | 否 | 1mo | 时间范围: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max |
| interval | str (enum) | 否 | 1d | K线间隔: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo |

### 响应参数

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| close | str | 收盘价 |
| date | str | 日期 |
| high | str | 最高价 |
| low | str | 最低价 |
| open | str | 开盘价 |
| volume | str | 成交量 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": [
    {
      "date": "2025-11-17T00:00:00-05:00",
      "open": 268.82000732421875,
      "high": 270.489990234375,
      "low": 265.7300109863281,
      "close": 267.4599914550781,
      "volume": 45018300
    },
    {
      "date": "2025-11-18T00:00:00-05:00",
      "open": 269.989990234375,
      "high": 270.7099914550781,
      "low": 265.32000732421875,
      "close": 267.44000244140625,
      "volume": 45677300
    }
  ]
}
```

---

## 3. 财务报表 (Financials)

**URL**: `/api/v1/yahoo/financials` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |
| type | str (enum) | 是 | - | 报表类型: balance (资产负债表), income (利润表), cashflow (现金流量表) |

### 响应参数

**注意**: 返回结构为 `Date -> {Fields}`。此处列出内部对象的字段。
| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| accountsPayable | float | 应付账款 |
| accountsReceivable | float | 应收账款 |
| accumulatedDepreciation | float | 累计折旧 |
| availableForSaleSecurities | float | 可供出售证券 |
| capitalLeaseObligations | any | 融资租赁义务 |
| capitalStock | float | 股本 |
| cashAndCashEquivalents | float | 现金及现金等价物 |
| cashCashEquivalentsAndShortTermInvestments | float | 现金及短期投资 |
| cashEquivalents | float | 现金等价物 |
| cashFinancial | float | 货币资金 |
| commercialPaper | float | 商业票据 |
| commonStock | float | 普通股 |
| commonStockEquity | float | 普通股权益 |
| currentAccruedExpenses | float | 流动应计费用 |
| currentAssets | float | 流动资产 |
| currentCapitalLeaseObligation | any | 一年内到期融资租赁 |
| currentDebt | float | 短期债务 |
| currentDebtAndCapitalLeaseObligation | float | 流动债务及租赁 |
| currentDeferredLiabilities | float | 流动递延负债 |
| currentDeferredRevenue | float | 流动递延收入 |
| currentLiabilities | float | 流动负债 |
| gainsLossesNotAffectingRetainedEarnings | float | 不影响留存收益的损益 |
| grossPpe | float | 固定资产原值 |
| incomeTaxPayable | float | 应交所得税 |
| inventory | float | 存货 |
| investedCapital | float | 投入资本 |
| investmentinFinancialAssets | float | 金融资产投资 |
| investmentsAndAdvances | float | 投资及垫款 |
| landAndImprovements | float | 土地及改良 |
| leases | float | 租赁负债 |
| longTermCapitalLeaseObligation | any | 长期融资租赁 |
| longTermDebt | float | 长期债务 |
| longTermDebtAndCapitalLeaseObligation | float | 长期债务及租赁 |
| machineryFurnitureEquipment | float | 机器设备及家具 |
| netDebt | float | 净债务 |
| netPpe | float | 固定资产净值 |
| netTangibleAssets | float | 有形资产净值 |
| nonCurrentDeferredAssets | float | 非流动递延资产 |
| nonCurrentDeferredTaxesAssets | float | 非流动递延所得税资产 |
| ordinarySharesNumber | float | 普通股数量 |
| otherCurrentAssets | float | 其他流动资产 |
| otherCurrentBorrowings | float | 其他短期借款 |
| otherCurrentLiabilities | float | 其他流动负债 |
| otherEquityAdjustments | float | 其他权益调整 |
| otherInvestments | any | 其他投资 |
| otherNonCurrentAssets | float | 其他非流动资产 |
| otherNonCurrentLiabilities | float | 其他非流动负债 |
| otherProperties | any | 其他房产 |
| otherReceivables | float | 其他应收款 |
| otherShortTermInvestments | float | 其他短期投资 |
| payables | float | 应付款项 |
| payablesAndAccruedExpenses | float | 应付及应计费用 |
| properties | float | 房产 |
| receivables | float | 应收款项 |
| retainedEarnings | float | 留存收益 |
| shareIssued | float | 已发行股份 |
| stockholdersEquity | float | 股东权益 |
| tangibleBookValue | float | 有形资产账面价值 |
| totalAssets | float | 总资产 |
| totalCapitalization | float | 总资本化 |
| totalDebt | float | 总债务 |
| totalEquityGrossMinorityInterest | float | 权益合计(含少数股东) |
| totalLiabilitiesNetMinorityInterest | float | 总负债 |
| totalNonCurrentAssets | float | 非流动资产合计 |
| totalNonCurrentLiabilitiesNetMinorityInterest | float | 非流动负债合计 |
| totalTaxPayable | float | 应交税费合计 |
| tradeandOtherPayablesNonCurrent | any | 长期应付及其他 |
| treasurySharesNumber | any | 库存股数量 |
| workingCapital | float | 营运资本 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": {
    "20250930": {
      "treasurySharesNumber": null,
      "ordinarySharesNumber": 14773260000.0,
      "shareIssued": 14773260000.0,
      "netDebt": 62723000000.0,
      "totalDebt": 98657000000.0,
      "tangibleBookValue": 73733000000.0,
      "investedCapital": 172390000000.0,
      "workingCapital": -17674000000.0,
      "netTangibleAssets": 73733000000.0,
      "capitalLeaseObligations": null,
      "commonStockEquity": 73733000000.0,
      "totalCapitalization": 152061000000.0,
      "totalEquityGrossMinorityInterest": 73733000000.0,
      "stockholdersEquity": 73733000000.0,
      "gainsLossesNotAffectingRetainedEarnings": -5571000000.0,
      "otherEquityAdjustments": -5571000000.0,
      "retainedEarnings": -14264000000.0,
      "capitalStock": 93568000000.0,
      "commonStock": 93568000000.0,
      "totalLiabilitiesNetMinorityInterest": 285508000000.0,
      "totalNonCurrentLiabilitiesNetMinorityInterest": 119877000000.0,
      "otherNonCurrentLiabilities": 41549000000.0,
      "tradeandOtherPayablesNonCurrent": null,
      "longTermDebtAndCapitalLeaseObligation": 78328000000.0,
      "longTermCapitalLeaseObligation": null,
      "longTermDebt": 78328000000.0,
      "currentLiabilities": 165631000000.0,
      "otherCurrentLiabilities": 44452000000.0,
      "currentDeferredLiabilities": 9055000000.0,
      "currentDeferredRevenue": 9055000000.0,
      "currentDebtAndCapitalLeaseObligation": 20329000000.0,
      "currentCapitalLeaseObligation": null,
      "currentDebt": 20329000000.0,
      "otherCurrentBorrowings": 12350000000.0,
      "commercialPaper": 7979000000.0,
      "payablesAndAccruedExpenses": 91795000000.0,
      "currentAccruedExpenses": 8919000000.0,
      "payables": 82876000000.0,
      "totalTaxPayable": 13016000000.0,
      "incomeTaxPayable": 13016000000.0,
      "accountsPayable": 69860000000.0,
      "totalAssets": 359241000000.0,
      "totalNonCurrentAssets": 211284000000.0,
      "otherNonCurrentAssets": 62950000000.0,
      "nonCurrentDeferredAssets": 20777000000.0,
      "nonCurrentDeferredTaxesAssets": 20777000000.0,
      "investmentsAndAdvances": 77723000000.0,
      "otherInvestments": null,
      "investmentinFinancialAssets": 77723000000.0,
      "availableForSaleSecurities": 77723000000.0,
      "netPpe": 49834000000.0,
      "accumulatedDepreciation": -76014000000.0,
      "grossPpe": 125848000000.0,
      "leases": 15091000000.0,
      "otherProperties": null,
      "machineryFurnitureEquipment": 83420000000.0,
      "landAndImprovements": 27337000000.0,
      "properties": 0.0,
      "currentAssets": 147957000000.0,
      "otherCurrentAssets": 14585000000.0,
      "inventory": 5718000000.0,
      "receivables": 72957000000.0,
      "otherReceivables": 33180000000.0,
      "accountsReceivable": 39777000000.0,
      "cashCashEquivalentsAndShortTermInvestments": 54697000000.0,
      "otherShortTermInvestments": 18763000000.0,
      "cashAndCashEquivalents": 35934000000.0,
      "cashEquivalents": 7667000000.0,
      "cashFinancial": 28267000000.0
    },
    "20240930": {
      "treasurySharesNumber": null,
      "ordinarySharesNumber": 15116786000.0,
      "shareIssued": 15116786000.0,
      "netDebt": 76686000000.0,
      "totalDebt": 106629000000.0,
      "tangibleBookValue": 56950000000.0,
      "investedCapital": 163579000000.0,
      "workingCapital": -23405000000.0,
      "netTangibleAssets": 56950000000.0,
      "capitalLeaseObligations": null,
      "commonStockEquity": 56950000000.0,
      "totalCapitalization": 142700000000.0,
      "totalEquityGrossMinorityInterest": 56950000000.0,
      "stockholdersEquity": 56950000000.0,
      "gainsLossesNotAffectingRetainedEarnings": -7172000000.0,
      "otherEquityAdjustments": -7172000000.0,
      "retainedEarnings": -19154000000.0,
      "capitalStock": 83276000000.0,
      "commonStock": 83276000000.0,
      "totalLiabilitiesNetMinorityInterest": 308030000000.0,
      "totalNonCurrentLiabilitiesNetMinorityInterest": 131638000000.0,
      "otherNonCurrentLiabilities": 45888000000.0,
      "tradeandOtherPayablesNonCurrent": 9254000000.0,
      "longTermDebtAndCapitalLeaseObligation": 85750000000.0,
      "longTermCapitalLeaseObligation": null,
      "longTermDebt": 85750000000.0,
      "currentLiabilities": 176392000000.0,
      "otherCurrentLiabilities": 44024000000.0,
      "currentDeferredLiabilities": 8249000000.0,
      "currentDeferredRevenue": 8249000000.0,
      "currentDebtAndCapitalLeaseObligation": 20879000000.0,
      "currentCapitalLeaseObligation": null,
      "currentDebt": 20879000000.0,
      "otherCurrentBorrowings": 10912000000.0,
      "commercialPaper": 9967000000.0,
      "payablesAndAccruedExpenses": 103240000000.0,
      "currentAccruedExpenses": null,
      "payables": 95561000000.0,
      "totalTaxPayable": 26601000000.0,
      "incomeTaxPayable": 26601000000.0,
      "accountsPayable": 68960000000.0,
      "totalAssets": 364980000000.0,
      "totalNonCurrentAssets": 211993000000.0,
      "otherNonCurrentAssets": 55335000000.0,
      "nonCurrentDeferredAssets": 19499000000.0,
      "nonCurrentDeferredTaxesAssets": 19499000000.0,
      "investmentsAndAdvances": 91479000000.0,
      "otherInvestments": null,
      "investmentinFinancialAssets": 91479000000.0,
      "availableForSaleSecurities": 91479000000.0,
      "netPpe": 45680000000.0,
      "accumulatedDepreciation": -73448000000.0,
      "grossPpe": 119128000000.0,
      "leases": 14233000000.0,
      "otherProperties": null,
      "machineryFurnitureEquipment": 80205000000.0,
      "landAndImprovements": 24690000000.0,
      "properties": 0.0,
      "currentAssets": 152987000000.0,
      "otherCurrentAssets": 14287000000.0,
      "inventory": 7286000000.0,
      "receivables": 66243000000.0,
      "otherReceivables": 32833000000.0,
      "accountsReceivable": 33410000000.0,
      "cashCashEquivalentsAndShortTermInvestments": 65171000000.0,
      "otherShortTermInvestments": 35228000000.0,
      "cashAndCashEquivalents": 29943000000.0,
      "cashEquivalents": 2744000000.0,
      "cashFinancial": 27199000000.0
    }
  }
}
```

---

## 4. 股票搜索 (Search)

**URL**: `/api/v1/yahoo/search` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| query | str | 是 | - | 搜索关键词 (如 Apple, 600519) |

### 响应参数 (results item)

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| exchange | str | 交易所 |
| longname | str | 公司全称 |
| shortname | str | 公司简称 |
| symbol | str | 股票代码 |
| type | str | 类型 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": {
    "query": "Apple",
    "count": 5,
    "results": [
      {
        "symbol": "AAPL",
        "shortname": "Apple Inc.",
        "longname": "Apple Inc.",
        "exchange": "NMS",
        "type": "EQUITY"
      },
      {
        "symbol": "APLE",
        "shortname": "Apple Hospitality REIT, Inc.",
        "longname": "Apple Hospitality REIT, Inc.",
        "exchange": "NYQ",
        "type": "EQUITY"
      },
      {
        "symbol": "AAPL.BA",
        "shortname": "APPLE INC CEDEAR(REPR 1/20 SHR)",
        "longname": "Apple Inc.",
        "exchange": "BUE",
        "type": "EQUITY"
      },
      {
        "symbol": "APC.DE",
        "shortname": "Apple Inc.                    R",
        "longname": "Apple Inc.",
        "exchange": "GER",
        "type": "EQUITY"
      },
      {
        "symbol": "AAPL.MX",
        "shortname": "APPLE INC",
        "longname": "Apple Inc.",
        "exchange": "MEX",
        "type": "EQUITY"
      }
    ]
  }
}
```

---

## 5. 股票新闻 (News)

**URL**: `/api/v1/yahoo/news` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |

### 响应参数

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| content | str | 新闻内容/摘要 |
| id | str | 标识符ID |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": [
    {
      "id": "982e6adc-3347-3edc-874a-ec04df02ce1d",
      "content": {
        "id": "982e6adc-3347-3edc-874a-ec04df02ce1d",
        "contenttype": "VIDEO",
        "title": "OpenAI’s hardware push could reshape the AI trade",
        "description": "<p><strong>Opening Bid Unfiltered is available on </strong><a data-i13n=\"cpos:1;pos:1\" href=\"https://podcasts.apple.com/us/podcast/opening-bid/id1749109417\"><strong>Apple Podcasts</strong></a><strong>, </strong><a data-i13n=\"cpos:2;pos:1\" href=\"https://open.spotify.com/show/6blmkje6G8vLF8cVSWxa5A\"><strong>Spotify</strong></a><strong>, </strong><a data-i13n=\"cpos:3;pos:1\" href=\"https://youtube.com/playlist?list=PLx28zU8ctIRrPPoWZxI2uK-uEGDIx0DDD&feature=shared\"><strong>YouTube</strong></a><strong>, or wherever you get your podcasts.</strong></p>\n<p>There has been one company at the very center of the AI trade this year. That is none other than OpenAI (<a data-i13n=\"cpos:4;pos:1\" href=\"https://finance.yahoo.com/quote/OPAI.PVT\">OPAI.PVT</a>)! OpenAI has won Yahoo Finance’s 11th annual Company of the Year award. Lost in the dizzying array of daily headlines from OpenAI is the fact that it may debut a hardware device within the next two years. Some are speculating it could be a challenger to the Apple (<a data-i13n=\"cpos:5;pos:1\" href=\"https://finance.yahoo.com/quote/AAPL\">AAPL</a>) iPhone. Why? OpenAI, in May, bought Jony Ive's AI devices startup io for approximately $6.4 billion in an all-equity deal. I've worked closely with Apple co-founder Steve Jobs to develop the iPhone. Yahoo Finance Executive Editor Brian Sozzi spoke exclusively with OpenAI CFO Sarah Friar about the company’s path forward, which could include a fascinating new hardware device.</p>\n<p><a data-i13n=\"cpos:6;pos:1\" href=\"https://open.spotify.com/show/6blmkje6G8vLF8cVSWxa5A?si=13c787846e704eaa\">Listen</a> on your favorite podcast platform or<a data-i13n=\"cpos:7;pos:1\" href=\"https://finance.yahoo.com/videos/series/opening-bid/\"> watch</a> on our website for full episodes of Opening Bid Unfiltered.</p>\n<p><em>Yahoo Finance's Opening Bid Unfiltered is produced by Langston Sessoms.</em></p>",
        "summary": "Opening Bid Unfiltered is available on Apple Podcasts, Spotify, YouTube, or wherever you get your podcasts. There has been one company at the very center of the AI trade this year. That is none other than OpenAI (OPAI.PVT)! OpenAI has won Yahoo Finance’s 11th annual Company of the Year award. Lost in the dizzying array of daily headlines from OpenAI is the fact that it may debut a hardware device within the next two years. Some are speculating it could be a challenger to the Apple (AAPL) iPhone. Why? OpenAI, in May, bought Jony Ive's AI devices startup io for approximately $6.4 billion in an all-equity deal. I've worked closely with Apple co-founder Steve Jobs to develop the iPhone. Yahoo Finance Executive Editor Brian Sozzi spoke exclusively with OpenAI CFO Sarah Friar about the company’s path forward, which could include a fascinating new hardware device. Listen on your favorite podcast platform or watch on our website for full episodes of Opening Bid Unfiltered. Yahoo Finance's Opening Bid Unfiltered is produced by Langston Sessoms.",
        "pubdate": "2025-12-15T11:58:25Z",
        "displaytime": "",
        "ishosted": true,
        "bypassmodal": false,
        "previewurl": null,
        "thumbnail": {
          "originalurl": "https://s.yimg.com/os/creatr-uploaded-images/2025-12/eda15a50-d79c-11f0-bfff-b905aef1e72b",
          "originalwidth": 1920,
          "originalheight": 1080,
          "caption": "",
          "resolutions": [
            {
              "url": "https://s.yimg.com/uu/api/res/1.2/0HQ4xuPaMW1pYMIE8e0B0g--~B/aD0xMDgwO3c9MTkyMDthcHBpZD15dGFjaHlvbg--/https://s.yimg.com/os/creatr-uploaded-images/2025-12/eda15a50-d79c-11f0-bfff-b905aef1e72b",
              "width": 1920,
              "height": 1080,
              "tag": "original"
            },
            {
              "url": "https://s.yimg.com/uu/api/res/1.2/SS4ly98XzykbU6vG8XpsUw--~B/Zmk9c3RyaW07aD0xMjg7dz0xNzA7YXBwaWQ9eXRhY2h5b24-/https://s.yimg.com/os/creatr-uploaded-images/2025-12/eda15a50-d79c-11f0-bfff-b905aef1e72b",
              "width": 170,
              "height": 128,
              "tag": "170x128"
            }
          ]
        },
        "provider": {
          "displayname": "Yahoo Finance Video",
          "url": "https://finance.yahoo.com/"
        },
        "canonicalurl": {
          "url": "https://finance.yahoo.com/video/openai-hardware-push-could-reshape-160025101.html",
          "site": "finance",
          "region": "US",
          "lang": "en-US"
        },
        "clickthroughurl": {
          "url": "https://finance.yahoo.com/video/openai-hardware-push-could-reshape-160025101.html",
          "site": "finance",
          "region": "US",
          "lang": "en-US"
        },
        "metadata": {
          "editorspick": true
        },
        "finance": {
          "premiumfinance": {
            "ispremiumnews": false,
            "ispremiumfreenews": false
          }
        },
        "storyline": null
      }
    }
  ]
}
```

---

## 6. 股东信息 (Holders)

**URL**: `/api/v1/yahoo/holders` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |

### 响应参数

**majorHolders / institutionalHolders** 结构:

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| dateReported | str | 报告日期 |
| holder | str | 持有机构/人 |
| pctchange | str | 持仓变动比例 |
| pctheld | str | 持仓比例 |
| shares | str | 持股数量 |
| value | str | 持仓市值 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": {
    "majorHolders": [
      {
        "value": 0.016970001
      },
      {
        "value": 0.64404
      },
      {
        "value": 0.65516
      },
      {
        "value": 7073.0
      }
    ],
    "institutionalHolders": [
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Vanguard Group Inc",
        "pctheld": 0.0947,
        "shares": 1399427162,
        "value": 381126992143,
        "pctchange": -0.0117
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Blackrock Inc.",
        "pctheld": 0.0776,
        "shares": 1146332274,
        "value": 312197864561,
        "pctchange": -0.0022
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "State Street Corporation",
        "pctheld": 0.0404,
        "shares": 597501113,
        "value": 162726441349,
        "pctchange": -0.0062
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "JPMORGAN CHASE & CO",
        "pctheld": 0.032,
        "shares": 473311062,
        "value": 128903901758,
        "pctchange": 1.2055
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Geode Capital Management, LLC",
        "pctheld": 0.0241,
        "shares": 356166414,
        "value": 97000142455,
        "pctchange": 0.004
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "FMR, LLC",
        "pctheld": 0.020499999,
        "shares": 303254081,
        "value": 82589733060,
        "pctchange": -0.0114
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Berkshire Hathaway, Inc",
        "pctheld": 0.0161,
        "shares": 238212764,
        "value": 64876055502,
        "pctchange": -0.1492
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Morgan Stanley",
        "pctheld": 0.0155,
        "shares": 229103384,
        "value": 62395161395,
        "pctchange": -0.0176
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Price (T.Rowe) Associates Inc",
        "pctheld": 0.014400001,
        "shares": 212755053,
        "value": 57942775168,
        "pctchange": 0.0495
      },
      {
        "dateReported": "2025-06-30T00:00:00.000",
        "holder": "NORGES BANK",
        "pctheld": 0.0128,
        "shares": 189804820,
        "value": 51692393934,
        "pctchange": 0.014099999
      }
    ],
    "mutualfundHolders": [
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "VANGUARD INDEX FUNDS-Vanguard Total Stock Market Index Fund",
        "pctheld": 0.031600002,
        "shares": 467135722,
        "value": 127222078778,
        "pctchange": -0.0274
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "VANGUARD INDEX FUNDS-Vanguard 500 Index Fund",
        "pctheld": 0.0248,
        "shares": 366145920,
        "value": 99718011029,
        "pctchange": -0.1363
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Fidelity Concord Street Trust-Fidelity 500 Index Fund",
        "pctheld": 0.0127,
        "shares": 187913047,
        "value": 51177179014,
        "pctchange": -0.0091
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "iShares Trust-iShares Core S&P 500 ETF",
        "pctheld": 0.0123000005,
        "shares": 182136844,
        "value": 49604059001,
        "pctchange": 0.0134000005
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "SPDR S&P 500 ETF TRUST",
        "pctheld": 0.0117999995,
        "shares": 174986129,
        "value": 47656597516,
        "pctchange": -0.0299
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "VANGUARD INDEX FUNDS-Vanguard Growth Index Fund",
        "pctheld": 0.0095,
        "shares": 140904646,
        "value": 38374675986,
        "pctchange": -0.0471
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "Invesco QQQ Trust, Series 1",
        "pctheld": 0.0084,
        "shares": 124773851,
        "value": 33981534602,
        "pctchange": 0.0041
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "VANGUARD INSTITUTIONAL INDEX FUNDS-Vanguard Institutional Index Fund",
        "pctheld": 0.0058999998,
        "shares": 86511134,
        "value": 23560874894,
        "pctchange": -0.055
      },
      {
        "dateReported": "2025-08-31T00:00:00.000",
        "holder": "VANGUARD WORLD FUND-Vanguard Information Technology Index Fund",
        "pctheld": 0.0045,
        "shares": 66163735,
        "value": 18019362489,
        "pctchange": -0.10609999
      },
      {
        "dateReported": "2025-09-30T00:00:00.000",
        "holder": "iShares Trust-iShares Russell 1000 Growth ETF",
        "pctheld": 0.0036000002,
        "shares": 53561374,
        "value": 14587172467,
        "pctchange": -0.0347
      }
    ]
  }
}
```

---

## 7. 分析师评级 (Analysis)

**URL**: `/api/v1/yahoo/analysis` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |

### 响应参数

**recommendationsSummary** 结构:

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| buy | str | 买入数 |
| hold | str | 持有数 |
| period | str | 周期 |
| sell | str | 卖出数 |
| strongbuy | str | 强力买入数 |
| strongsell | str | 强力卖出数 |

**upgradesDowngrades** 结构:

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| action | str | 变动动作 |
| currentpricetarget | str | 最新目标价 |
| firm | str | 机构名称 |
| fromgrade | str | 原评级 |
| pricetargetaction | str | 目标价调整 |
| priorpricetarget | str | 前次目标价 |
| tograde | str | 新评级 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": {
    "recommendations": [
      {
        "period": "0m",
        "strongbuy": 5,
        "buy": 24,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      },
      {
        "period": "-1m",
        "strongbuy": 5,
        "buy": 24,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      },
      {
        "period": "-2m",
        "strongbuy": 5,
        "buy": 24,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      },
      {
        "period": "-3m",
        "strongbuy": 5,
        "buy": 23,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      }
    ],
    "recommendationsSummary": [
      {
        "period": "0m",
        "strongbuy": 5,
        "buy": 24,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      },
      {
        "period": "-1m",
        "strongbuy": 5,
        "buy": 24,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      },
      {
        "period": "-2m",
        "strongbuy": 5,
        "buy": 24,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      },
      {
        "period": "-3m",
        "strongbuy": 5,
        "buy": 23,
        "hold": 15,
        "sell": 1,
        "strongsell": 3
      }
    ],
    "targetMean": 286.57584,
    "upgradesDowngrades": [
      {
        "firm": "Citigroup",
        "tograde": "Buy",
        "fromgrade": "Buy",
        "action": "main",
        "pricetargetaction": "Raises",
        "currentpricetarget": 330.0,
        "priorpricetarget": 315.0
      },
      {
        "firm": "Evercore ISI Group",
        "tograde": "Outperform",
        "fromgrade": "Outperform",
        "action": "main",
        "pricetargetaction": "Raises",
        "currentpricetarget": 325.0,
        "priorpricetarget": 300.0
      },
      {
        "firm": "Wedbush",
        "tograde": "Outperform",
        "fromgrade": "Outperform",
        "action": "main",
        "pricetargetaction": "Raises",
        "currentpricetarget": 350.0,
        "priorpricetarget": 320.0
      },
      {
        "firm": "CLSA",
        "tograde": "Outperform",
        "fromgrade": "Outperform",
        "action": "main",
        "pricetargetaction": "Raises",
        "currentpricetarget": 330.0,
        "priorpricetarget": 265.0
      },
      {
        "firm": "Loop Capital",
        "tograde": "Buy",
        "fromgrade": "Buy",
        "action": "main",
        "pricetargetaction": "Raises",
        "currentpricetarget": 325.0,
        "priorpricetarget": 315.0
      }
    ]
  }
}
```

---

## 8. 公司日历 (Calendar)

**URL**: `/api/v1/yahoo/calendar` (POST)

### 请求参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| symbol | str | 是 | - | 股票代码 (如 AAPL) |

### 响应参数 (calendar object)

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| dividendDate | str | 派息日 |
| earningsAverage | float | 平均每股收益 |
| earningsDate | list | 日期/时间戳 |
| earningsHigh | float | 最高每股收益 |
| earningsLow | float | 最低每股收益 |
| exdividendDate | str | 除息日 |
| revenueAverage | int | 平均营收预测 |
| revenueHigh | int | 最高营收预测 |
| revenueLow | int | 最低营收预测 |

### 示例响应

```json
{
  "code": "200000",
  "message": "success",
  "data": {
    "calendar": {
      "dividendDate": "2025-11-13",
      "exdividendDate": "2025-11-10",
      "earningsDate": [
        "2026-01-29"
      ],
      "earningsHigh": 2.76,
      "earningsLow": 2.51,
      "earningsAverage": 2.66263,
      "revenueHigh": 140666000000,
      "revenueLow": 136679500000,
      "revenueAverage": 138088283540
    }
  }
}
```

---

## 9. 批量获取股票基础信息 (Batch Stock Base Data)

**URL**: `/api/v1/yahoo/batch/get_stock_base_data` (POST)

### 请求参数

**注意**: 该接口接收一个 JSON 对象，包含 `is_return_history` 和 `stock_list`。

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| is_return_history | bool | 否 | false | 是否返回历史K线数据 |
| stock_list | list[object] | 是 | - | 股票列表 |

**stock_list 内部对象参数**:

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| stock_symbol | str | 是 | 股票代码 (如 600519) |
| exchange_acronym | str | 是 | 交易所简称 (如 SSE, NASDAQ) |

**示例请求体**:
```json
{
  "is_return_history": false,
  "stock_list": [
    {
      "stock_symbol": "AAPL",
      "exchange_acronym": "NASDAQ"
    },
    {
      "stock_symbol": "601933",
      "exchange_acronym": "SSE"
    }
  ]
}
```

### 响应参数 (List Item)

包含股票基本信息、市场数据、最新的交易数据以及计算出的各周期收益率。如果 `is_return_history` 为 `true`，`history` 字段将包含最近 5 年的历史数据。

| 字段名 | 类型 | 说明 |
| :--- | :--- | :--- |
| stock_symbol | str | 股票代码 |
| exchange_acronym | str | 交易所简称 |
| name | str | 股票名称 |
| currency | str | 货币 |
| exchange_timezone_name | str | 交易所时区名 |
| exchange_timezone_short_name | str | 交易所时区简称 |
| gmt_off_set_milliseconds | int | 时区偏移(毫秒) |
| quote_type | str | 证券类型 |
| market_state | str | 市场状态 |
| regular_market_price | float | 常规市场价格 |
| regular_market_previous_close | float | 常规市场昨收 |
| regular_market_open | float | 常规市场开盘 |
| regular_market_day_high | float | 常规市场最高 |
| regular_market_day_low | float | 常规市场最低 |
| regular_market_volume | int | 常规市场成交量 |
| bid | float | 买一价 |
| ask | float | 卖一价 |
| market_cap | int | 市值 |
| beta | float | Beta系数 |
| trailing_pe | float | 滚动市盈率 (TTM) |
| forward_pe | float | 远期市盈率 |
| eps_trailing_twelve_months | float | 滚动EPS (TTM) |
| eps_forward | float | 远期EPS |
| fifty_two_week_low | float | 52周最低 |
| fifty_two_week_high | float | 52周最高 |
| fifty_two_week_change_percent | float | 52周涨跌幅 |
| all_time_high | float | 历史最高 |
| all_time_low | float | 历史最低 |
| average_volume_10_days | int | 10日平均成交量 |
| average_volume_3_month | int | 3月平均成交量 |
| dividend_yield | float | 股息率 |
| dividend_rate | float | 股息 |
| trailing_annual_dividend_yield | float | 滚动年度股息率 |
| shares_outstanding | int | 总股本 |
| float_shares | int | 流通股 |
| held_percent_insiders | float | 内部持股比例 |
| held_percent_institutions | float | 机构持股比例 |
| short_ratio | float | 做空比率 |
| year_to_date_return | float |年初至今收益率 |
| year_to_date_trading_date_range | str | 年初至今交易日区间 (Start:End) |
| three_month_return | float | 近3月收益率 |
| three_month_trading_date_range | str | 近3月交易日区间 |
| six_month_return | float | 近6月收益率 |
| six_month_trading_date_range | str | 近6月交易日区间 |
| one_year_return | float | 近1年收益率 |
| one_year_trading_date_range | str | 近1年交易日区间 |
| three_year_return | float | 近3年收益率 |
| three_year_trading_date_range | str | 近3年交易日区间 |
| five_year_return | float | 近5年收益率 |
| five_year_trading_date_range | str | 近5年交易日区间 |
| company_officers | list | 高管列表 |
| history | list | 历史K线 (可选) |

### 示例响应

```json
[
    {
        "stock_symbol": "AAPL",
        "exchange_acronym": "NASDAQ",
        "name": "Apple",
        "currency": "USD",
        "exchange_timezone_name": "America/New_York",
        "exchange_timezone_short_name": "EST",
        "quote_type": "EQUITY",
        "market_state": "REGULAR",
        "regular_market_price": 192.53,
        "year_to_date_return": 0.48,
        "year_to_date_trading_date_range": "2023-01-03:2023-12-29",
        "history": null
    }
]
```