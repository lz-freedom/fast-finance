from fastapi import APIRouter
from app.schemas.response import BaseResponse

router = APIRouter()

@router.get("/health", response_model=BaseResponse, summary="健康检查", tags=["Health"])
async def health_check():
    """
    检查服务是否运行正常
    """
    return BaseResponse.success(data={"status": "ok", "message": "Service is running"})
