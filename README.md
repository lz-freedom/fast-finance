# Fast Finance API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**高性能、易扩展的金融数据 API 网关**

[快速开始](#快速开始) • [文档](#API-文档) • [配置](#配置说明) • [贡献](#贡献指南)

</div>

---

## 📖 项目简介

**Fast Finance API** 是一个基于 **FastAPI** 构建的现代化异步后端服务，旨在为金融应用提供统一、高效的数据接口。它封装了 **TradingView 技术分析** 和 **Yahoo Finance 基本面数据**，屏蔽了上游接口的复杂性，并提供标准化的 RESTful API。

### 核心特性

- ⚡ **高性能异步架构**: 基于 FastAPI 和 Uvicorn，充分利用 Python 异步特性。
- 🐳 **容器化部署**: 提供完整的 Docker 和 Docker Compose 支持，开箱即用。
- 🛡️ **健壮的工程实践**: 集成 Pydantic 类型检查、统一异常处理、标准化响应格式。
- 🔌 **多源数据集成**:
    - **TradingView**: 实时技术指标分析 (TA)、筛选器数据。
    - **Yahoo Finance**: 全面的股票基本面、K线、财报、新闻数据。

## 🏗️ 系统架构

```mermaid
graph TD
    Client[客户端 (Web/Mobile)] -->|HTTP/REST| LB[Nginx / Load Balancer]
    LB -->|Proxy| API[Fast Finance API]
    
    subgraph "Core Services"
        API -->|Route| TV[TradingView Service]
        API -->|Route| YF[Yahoo Finance Service]
        API -->|Config| Settings[Pydantic Settings]
    end
    
    subgraph "Data Sources (External)"
        TV -->|HTTP Requests| TVAPI[TradingView Server]
        YF -->|yfinance Lib| YFAPI[Yahoo Finance API]
    end
    
    style API fill:#009688,stroke:#fff,stroke-width:2px,color:#fff
    style TV fill:#f9f,stroke:#333,stroke-width:2px
    style YF fill:#bbf,stroke:#333,stroke-width:2px
```

## 🚀 快速开始

### 前置条件
- **Docker** & **Docker Compose** (推荐)
- Python 3.10+ (仅本地开发需要)

### 方式一：Docker 容器化运行 (推荐)

最简单、最稳定的运行方式。

1. **构建并启动服务**
   ```bash
   docker-compose up -d --build
   ```

2. **验证服务**
   访问健康检查接口：`http://localhost:9130/api/v1/system/health`

3. **查看日志**
   ```bash
   docker-compose logs -f app
   ```

4. **停止服务**
   ```bash
   docker-compose down
   ```

### 方式二：本地开发运行

适用于开发调试和代码贡献。

1. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **启动热重载服务器**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 9130
   ```

## 📚 API 文档

本项目提供交互式 Swagger UI 文档，启动服务后即可访问。

- **在线文档 (Swagger UI)**: [http://localhost:9130/docs](http://localhost:9130/docs)
- **详细接口定义**: 请参阅 [API_DOC.md](./API_DOC.md) 获取完整的请求/响应示例和字段说明。

### 接口概览

| 模块 | 路径前缀 | 描述 |
| :--- | :--- | :--- |
| **System** | `/api/v1/system` | 健康检查、系统状态 |
| **TradingView** | `/api/v1/tradingview` | 技术分析指标、市场筛选、标的搜索 |
| **Yahoo Finance** | `/api/v1/yahoo` | 股票详情、K线历史、财报、新闻、股东分析 |

## ⚙️ 配置说明

项目配置通过环境变量管理，支持 `.env` 文件。

| 变量名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `API_V1_STR` | `/api/v1` | API 路径版本前缀 |
| `PROJECT_NAME` | `Fast Finance API` | Swagger 文档标题 |
| `BACKEND_CORS_ORIGINS` | `[]` | 允许跨域的源列表 (JSON 数组格式) |
| `LOG_LEVEL` | `INFO` | 日志级别 (DEBUG, INFO, WARNING, ERROR) |
| `JSON_LOGS` | `False` | 是否启用 JSON 格式日志 |
| `DEBUG` | `True` | 是否开启调试模式 |
| `PORT` | `9130` | 服务监听端口 (Docker 内部) |

## 📂 项目结构

```text
fast-finance/
├── app/
│   ├── api/             # API 路由定义 (Endpoints)
│   ├── core/            # 核心配置 (Config, Logging, Middleware)
│   ├── schemas/         # Pydantic 数据模型 (DTOs)
│   ├── services/        # 业务逻辑层
│   └── main.py          # 应用入口
├── docs/                # 额外文档
├── tests/               # 测试用例
├── API_DOC.md           # 详细接口文档
├── Dockerfile           # Docker 构建文件
├── docker-compose.yml   # 容器编排配置
└── requirements.txt     # Python 依赖清单
```

## 🤝 贡献指南

1. Fork 本仓库。
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启 Pull Request。

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。
