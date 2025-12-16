from typing import Generic, TypeVar, Any, Optional
from pydantic import BaseModel

T = TypeVar("T")

class ResponseCode:
    SUCCESS = "200000"
    BAD_REQUEST = "400000"
    UNAUTHORIZED = "401000"
    FORBIDDEN = "403000"
    NOT_FOUND = "404000"
    INTERNAL_ERROR = "500000"
    VALIDATION_ERROR = "422000"

class BaseResponse(BaseModel, Generic[T]):
    code: str
    message: str = "success"
    data: Optional[T] = None

    @classmethod
    def success(cls, data: T = None, message: str = "success"):
        return cls(code=ResponseCode.SUCCESS, message=message, data=data)

    @classmethod
    def fail(cls, code: str, message: str, data: Any = None):
        return cls(code=code, message=message, data=data)
