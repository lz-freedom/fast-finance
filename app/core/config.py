import logging
import sys
from typing import Any, Optional

from pydantic import AnyHttpUrl, EmailStr, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Fast Finance API"
    
    # 跨域设置
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    
    # 代理设置
    PROXY_TRADINGVIEW: Optional[str] = None
    PROXY_YAHOO: Optional[str] = None

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # 日志设置
    LOG_LEVEL: str = "INFO"
    JSON_LOGS: bool = False
    DEBUG: bool = True
    
    # 服务端口 (容器内部使用，外部通过 Docker 映射)
    PORT: int = 9130

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
