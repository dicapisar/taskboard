import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.schemas.base_response import BaseResponse

router = APIRouter()

@router.post("", response_model=BaseResponse, status_code=200)
async def login(request: Request, cache_service: CacheService = Depends(get_cache_service)):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    session_id = request.cookies.get("session_id")

    await cache_service.delete(f"session:{session_id}")


    data_response = BaseResponse(
        success=True,
        message="Login successful",
        http_status_code= 200,
        data = None
    )

    return data_response