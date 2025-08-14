from fastapi import APIRouter, Depends, HTTPException

from src.app.schemas.base_response import BaseResponse
from src.app.schemas.user import UserCreate, UserOut
from src.app.services.user_service import UserService, get_user_service

router = APIRouter()

@router.post("", response_model=BaseResponse, status_code=201)
async def create_user(payload: UserCreate, user_service: UserService = Depends(get_user_service)):
    existing = await user_service.is_username_exists(payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    existing_email = await user_service.is_email_exists(payload.email.__str__())
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = await user_service.create_user(payload)

    data_response = BaseResponse(
        success=True,
        message="User created successfully",
        http_status_code=201,
        data={
            "user_id": user.id,
            "username": user.username,
            "email": user.email.__str__(),
            "is_admin": user.is_admin(),
        }
    )

    return data_response

@router.get("", response_model=BaseResponse, status_code=200)
async def list_users(user_service: UserService = Depends(get_user_service)):
    users = await user_service.list_users()

    if users is None:
        raise HTTPException(status_code=404, detail="User not found")

    data_response = BaseResponse(
        success=True,
        message="Users retrieved successfully",
        http_status_code=200,
        data=users
    )
    return data_response