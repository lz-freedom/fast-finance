# 开发日志

## 2025-12-22
- 将 Investing API (`/api/v1/investing`) 改为 POST 方法，并使用 Pydantic 模型接收参数。
- 统一 Investing API 返回结构，使用 `BaseResponse` (code, message, data) 格式。

## 2025-12-16
- 初始化项目记忆库。
- 构建 FastAPI 项目基础架构。
- 完成 Docker Compose 部署配置 (Host Port: 9130)。
- 验证服务运行正常。
- 重构 API 响应格式：
    - 统一返回 HTTP 200。
    - 定义 Standard Response Schema (`code`, `message`, `data`)。
    - 自定义异常处理器捕获 `HTTPException`, `StarletteHTTPException`, `RequestValidationError`。
- 集成 `tradingview_ta` 库：
    - 新增 `/api/v1/tradingview` 路由模块。
    - 实现 `analysis`, `analysis/multiple`, `search` 接口。
    - 深度调试与优化：
        - 使用 Monkey Patch (`patch_tradingview.py`) 注入 headers 解决请求被拒问题。
        - 重构 Schema 使用 `Enum` 规范 screener, interval 等参数。
        - 修复全局异常配置 (`DEBUG` 缺失)。
    - 更新 `README.md`，添加了完整的 TradingView API 使用指南和枚举参数列表。
    - 优化 Swagger 文档：为 Pydantic Schema 的字段添加了详细描述和示例值。
    - 修复 Search 接口后，进一步重构代码：
    - 彻底移除 `tradingview_ta` 第三方库依赖。
    - 在 `app/services/tradingview` 中实现了原生核心逻辑，包含 `Configurable Headers` 以原生解决 WAF 问题。
    - 重写了 API 层以调用新的 Service。
    - 修复了移除旧库导致的 `requests` 依赖缺失问题，并验证了所有接口。
