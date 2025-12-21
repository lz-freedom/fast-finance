# 使用官方 Python 3.10 轻量级镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
# 防止 Python 生成 .pyc 文件
ENV PYTHONDONTWRITEBYTECODE=1
# 确保日志即时输出
ENV PYTHONUNBUFFERED=1

# 安装系统依赖（如果需编译依赖可在此添加 build-essential 等）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建非 root 用户运行应用 (安全最佳实践)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# 暴露端口 (仅用于文档，实际由 docker-compose 或 run 命令映射)
EXPOSE 9130

# 启动命令
# host 0.0.0.0 确保容器外可访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9130"]
