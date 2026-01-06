from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    CustomException,
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from app.api.v1.endpoints import health
from app.api.v1.endpoints import yahoo
from app.api.v1.endpoints import investing
from app.api.v1.endpoints import google
from app.api.v1.endpoints import ai_help

# 初始化日志
setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        description="Fast Finance API Document. \n\n[> 定时任务管理面板 (Scheduler UI)](/static/scheduler.html)"
    )

    # CORS 配置
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 注册异常处理器
    app.add_exception_handler(CustomException, custom_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)

    # 注册路由
    # 这里简单直接引入，实际项目可能通过 api_router 统一管理
    app.include_router(health.router, prefix=f"{settings.API_V1_STR}/system")

    # 注册 Tools 路由
    from app.api.v1.endpoints import tools
    app.include_router(tools.router, prefix=f"{settings.API_V1_STR}/tools", tags=["工具"])

    # 注册 AI Help 路由
    app.include_router(ai_help.router, prefix=f"{settings.API_V1_STR}/ai_help", tags=["AI辅助"])

    # 注册 TradingView 路由
    from app.api.v1.endpoints import tradingview
    from app.api.v1.endpoints import tradingview
    app.include_router(tradingview.router, prefix=f"{settings.API_V1_STR}/tradingview", tags=["TradingView"])

    # 注册 TradingView Sync 路由
    from app.api.v1.endpoints import tradingview_sync
    app.include_router(tradingview_sync.router, prefix=f"{settings.API_V1_STR}/tools/tradingview-sync", tags=["TradingView 数据同步"])

    # 注册 Investing Sync 路由
    from app.api.v1.endpoints import tools_investing
    app.include_router(tools_investing.router, prefix=f"{settings.API_V1_STR}/tools/investing-sync", tags=["Investing 数据同步"])

    # 注册 Yahoo 路由
    app.include_router(yahoo.router, prefix=f"{settings.API_V1_STR}/yahoo", tags=["Yahoo Finance"])

    # 注册 Investing 路由
    app.include_router(investing.router, prefix=f"{settings.API_V1_STR}/investing", tags=["英为财情"])

    # 注册 Google 路由
    app.include_router(google.router, prefix=f"{settings.API_V1_STR}/google", tags=["Google Finance"])

    # 注册 Scheduler 路由
    from app.api.v1.endpoints import scheduler
    app.include_router(scheduler.router, prefix=f"{settings.API_V1_STR}/scheduler", tags=["定时任务"])

    # Mount Static Files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    static_dir = os.path.join(current_dir, "static")
    
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.on_event("startup")
    async def startup_event():
        try:
            from app.core.database import SQLiteManager
            from app.core.scheduler import SchedulerService
            
            # Initialize DB
            SQLiteManager.init_db()
            
            # Start Scheduler
            SchedulerService.start()
            
        except Exception as e:
            # Don't fail up just log
            print(f"Startup task failed: {e}")


    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    # 使用配置中的端口
    uvicorn.run(app, host="0.0.0.0", port=settings.PORT)
