# Fast Finance API

基于 FastAPI 构建的 Python 后端项目，支持 Docker 部署，集成 Swagger 文档与统一异常处理。

## 核心特性
- **FastAPI**: 高性能异步框架。
- **Docker Compose**: 一键部署。
- **统一响应格式**: 无论成功失败，HTTP 状态码均为 200，业务状态码封装在 `code` 字段。
- **配置管理**: Pydantic Settings 类型安全配置。

## 快速开始

### 前置条件
- Docker & Docker Compose
- (可选) Python 3.10+ (本地开发用)

### 方式一：Docker 运行 (推荐)

代码修改后，最简单的测试方式是使用 Docker：

1. **构建并启动服务**
   ```bash
   docker-compose up -d --build
   ```
   *注意：`--build` 参数确保你的代码修改被重新打包进镜像。*

2. **查看日志**
   ```bash
   docker-compose logs -f
   ```

3. **停止服务**
   ```bash
   docker-compose down
   ```

### 方式二：本地 Python 运行

如果你想更快的调试（利用热重载）：

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动开发服务器**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 9130
   ```
   *注意：代码保存后服务会自动重启。*

## 验证与测试

- **Swagger 文档**: [http://localhost:9130/docs](http://localhost:9130/docs)
- **健康检查**: [http://localhost:9130/api/v1/system/health](http://localhost:9130/api/v1/system/health)
  - 预期响应: `{"code": "200000", "message": "success", "data": {"status": "ok", ...}}`

## TradingView API 接口

我们在 `/api/v1/tradingview` 提供了技术分析接口。

### 1. 获取分析数据 (Analysis)
POST `/api/v1/tradingview/analysis`
获取单个标的的详细技术指标。

**请求参数**:
```json
{
  "symbol": "AAPL",
  "exchange": "NASDAQ",
  "screener": "america",
  "interval": "1d"
}
```

### 2. 批量获取分析数据 (Multiple Analysis)
POST `/api/v1/tradingview/analysis/multiple`
批量获取多个标的的分析数据（需在同一 Screener 下）。

**请求参数**:
```json
{
  "symbols": ["NASDAQ:AAPL", "NYSE:TSLA"],
  "screener": "america",
  "interval": "1h"
}
```

### 参数参考 (Enumeration)

**Screener (市场/国家)**
| 值 | 说明 |
| :--- | :--- |
| `america` | 美股 (USA) |
| `crypto` | 加密货币 |
| `forex` | 外汇 |
| `cfd` | 差价合约 |
| `indonesia`, `india`, `uk`, `brazil` | 其他国家股市... |

**Interval (时间周期)**
| 值 | 说明 |
| :--- | :--- |
| `1m` | 1 分钟 |
| `5m` | 5 分钟 |
| `15m` | 15 分钟 |
| `30m` | 30 分钟 |
| `1h` | 1 小时 |
| `2h` | 2 小时 |
| `4h` | 4 小时 |
| `1d` | 1 天 (默认) |
| `1W` | 1 周 |
| `1M` | 1 月 |

### 3. 搜索标的 (Search)
POST `/api/v1/tradingview/search`
搜索交易标的信息。

**请求参数**:
```json
{
  "text": "BTC",
  "type": "crypto" // 可选: stock, crypto, futures, forex, cfd, index
}
```
*(注意：此接口可能受 TradingView 上游限制而不稳定)*

## 项目结构

```text
fast-finance/
├── app/
│   ├── api/             # API 接口路由
│   ├── core/            # 核心配置 (config, logging, exceptions)
│   ├── schemas/         # Pydantic 模型 (req/resp schema)
│   └── main.py          # 应用入口
├── Dockerfile           # Docker 镜像构建
├── docker-compose.yml   # 容器编排
└── requirements.txt     # Python 依赖
```

## 常见操作 Q&A

**Q: 修改了端口怎么生效？**
A: 修改 `.env` 或 `docker-compose.yml` 中的端口配置，然后运行 `docker-compose up -d` 重新创建容器。

**Q: 增加了新的 Python 包？**
A: 
1. 将包名写入 `requirements.txt`。
2. 运行 `docker-compose up -d --build` 重新构建镜像。
