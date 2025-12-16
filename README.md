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
