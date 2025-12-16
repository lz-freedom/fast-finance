from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union, Any
from app.core.config import settings
from app.schemas.response import BaseResponse, ResponseCode

from starlette.exceptions import HTTPException as StarletteHTTPException

class CustomException(Exception):
    def __init__(self, code: str, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data

async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=200,
        content=BaseResponse.fail(code=exc.code, message=exc.message, data=exc.data).model_dump(),
    )

async def http_exception_handler(request: Request, exc: Union[HTTPException, StarletteHTTPException]):
    # 将 HTTP 状态码转换为类似 404000 的格式，或使用默认错误码
    # 简单映射：status_code * 1000
    custom_code = f"{exc.status_code}000"
    return JSONResponse(
        status_code=200,
        content=BaseResponse.fail(code=custom_code, message=exc.detail).model_dump(),
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content=BaseResponse.fail(
            code=ResponseCode.VALIDATION_ERROR, 
            message="Validation Error", 
            data=exc.errors() # Pydantic v2 use exc.errors() which returns simple dicts, safe to dump
        ).model_dump(),
    )

async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=200,
        content=BaseResponse.fail(
            code=ResponseCode.INTERNAL_ERROR, 
            message="Internal Server Error", 
            data=str(exc) if settings.DEBUG else None
        ).model_dump(),
    )
