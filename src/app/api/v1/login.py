import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import get_db
from src.app.schemas.login import Login
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.services.login_service import LoginService
from src.app.core.cache import redis
from src.app.schemas.base_response import BaseResponse

router = APIRouter()

@router.post("", response_model=BaseResponse, status_code=200)
async def login(response: Response, payload: Login, db: AsyncSession = Depends(get_db), cache_service: CacheService = Depends(get_cache_service)):
    service = LoginService(db)
    user = await service.authenticate_user(payload.email.__str__(), payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Store user ID in Redis cache for session management
    session_id = str(uuid.uuid4())
    session_data = {"user_id": user.id, "user_name": user.username, "email": user.email, "rol_id": user.role_id}
    await cache_service.set_user_session_data(session_id, user.to_user_detail())
    #await redis.set(f"session:{session_id}", json.dumps(session_data), ex=3600)
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
            "rol_id": user.role_id
        }
    )

    return data_response