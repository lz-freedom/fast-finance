# 2. 从 TradingView 获取数据遍历 Exchange

## 正在进行的任务
- [x] 创建 SQLite 表 `tradingview_stock`
- [x] 实现 TradingView 数据获取逻辑
- [x] 实现数据存储逻辑
- [x] 实现 API 接口 (全 POST + BaseResponse)
- [x] 新增 IPO 和 Sector 数据字段
- [x] 实现 API 参数过滤 `ipo_offer_date_type`
- [x] 修正数据库时间时区 (UTC+8)
- [x] 清理重复 Symbol (去除 .U 如果存在 .UN/.UM)
- [x] 强制重构接口为 POST 方法
- [x] 格式化 IPO 日期 (YYYY-MM-DD，修复负数时间戳问题)
- [x] API 命名和文档中文化
- [x] 支持 Investing.com 数据同步 (Tools 路由，中英双语，表结构)

## 任务上下文
用户要求新增 Investing.com 数据同步功能，并调整路由结构。
- 已创建 `investing_stock` 表，包含中英双语字段 (`name_cn`, `name_en` 等)。
- 已实现 `InvestingSyncService`，逻辑：先抓中文 (`domain-id: cn`)，再抓英文 (`domain-id: us`)，最后合并入库。
- 已新增 Tools 路由组 `/api/v1/tools/investing-sync`，并迁移 TradingView Sync 到 `/api/v1/tools/tradingview-sync`。
- 验证：数据已成功入库，中英文名称和行业信息一一对应。

## 下一步计划
任务已全部完成。等待新需求。
