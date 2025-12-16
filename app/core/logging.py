import logging
import sys
from app.core.config import settings

def setup_logging():
    """
    配置全局日志格式
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # 基础格式
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    
    # 清除旧的处理器，避免重复
    logger.handlers = []
    logger.addHandler(console_handler)
    
    # 设置 uvicorn 访问日志格式 (可选微调)
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").addHandler(console_handler) 
    # 注意：uvicorn 自身有比较复杂的配置，这里简单重定向到 stdout 统一管理
