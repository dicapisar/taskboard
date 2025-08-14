import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from src.app.schemas.login import Login
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.services.login_service import LoginService, get_login_service
from src.app.schemas.base_response import BaseResponse

router = APIRouter()

@router.post("", response_model=BaseResponse, status_code=200)
async def login(response: Response, payload: Login, cache_service: CacheService = Depends(get_cache_service), login_service: LoginService = Depends(get_login_service)):
    user = await login_service.authenticate_user(payload.email.__str__(), payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Store user ID in Redis cache for session management
    session_id = str(uuid.uuid4())
    await cache_service.set_user_session_data(session_id, user.to_user_detail())
    response.set_cookie("session_id", session_id, max_age=3600, httponly=True)

    data_response = BaseResponse(
        success=True,
        message="Login successful",
        http_status_code= 200,
        data = {
            "session_id": session_id,
            "user_id": user.id,
            "user_name": user.username,
            "email": user.email,
            "is_admin": user.is_admin(),
        }
    )

    return data_response