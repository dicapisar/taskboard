import os

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends

from src.app.dtos.user_detail import UserDetail
from src.app.schemas.base_response import BaseResponse
from src.app.schemas.user import UserUpdate, UserPasswordUpdate
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.services.user_service import UserService, get_user_service

UPLOAD_PROFILE_IMAGE_DIR = "src/app/static/img/profile_images/"

router = APIRouter()

@router.post("/profile_image", response_model=BaseResponse, status_code=201)
async def upload_profile_image(request: Request, file: UploadFile = File(...)):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")

    if not file.filename.endswith('.png'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNGis allowed.")

    if file.size > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 5 MB.")

    user_id = int(user_data_session["id"])

    user_profile_image_path = f"{UPLOAD_PROFILE_IMAGE_DIR}/{user_id}/"

    os.makedirs(user_profile_image_path, exist_ok=True)

    file_path = os.path.join(user_profile_image_path, "user.png")

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return BaseResponse(
        success=True,
        message="Profile image uploaded successfully",
        http_status_code=201,
        data=None
    )

@router.post("/user_details", response_model=BaseResponse, status_code=200)
async def update_user_details(request: Request, user_detail:  UserUpdate, user_service: UserService = Depends(get_user_service), cache_service: CacheService = Depends(get_cache_service)):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_name = user_data_session["username"]
    user_email = user_data_session["email"]
    user_id = int(user_data_session["id"])

    if user_detail.username == user_name and user_detail.email == user_email:
        raise HTTPException(status_code=400, detail="No changes detected in user details")

    if user_name != user_detail.username:
        user_name_exists = await user_service.is_username_exists(user_detail.username)
        if user_name_exists:
            raise HTTPException(status_code=400, detail="Username already exists")

    if user_email != user_detail.email:
        user_email_exists = await user_service.is_email_exists(user_detail.email.__str__())
        if user_email_exists:
            raise HTTPException(status_code=400, detail="Email already exists")


    await user_service.update_user_details(user_detail, user_id)

    # Update user session data in cache
    user_data_session["username"] = user_detail.username
    user_data_session["email"] = user_detail.email.__str__()
    session_id = request.cookies.get("session_id")

    user_detail = UserDetail(
        id=user_data_session["id"],
        username=user_detail.username,
        email=user_detail.email.__str__(),
        is_admin=user_data_session.get("is_admin", False),
    )

    await cache_service.set_user_session_data(session_id, user_detail)

    return BaseResponse(
        success=True,
        message="User details updated successfully",
        http_status_code=200,
        data=None
    )

@router.post("/password", response_model=BaseResponse, status_code=200)
async def update_password(request: Request, user_password_update: UserPasswordUpdate, user_service: UserService = Depends(get_user_service)):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    if not user_password_update.old_password or not user_password_update.new_password:
        raise HTTPException(status_code=400, detail="Old password and new password are required")

    if user_password_update.old_password == user_password_update.new_password:
        raise HTTPException(status_code=400, detail="Old password and new password cannot be the same")

    user_id = int(user_data_session["id"])

    await user_service.update_user_password(user_id, user_password_update.old_password, user_password_update.new_password)


    # Password update logic would go here
    # For now, we will just return a success message
    return BaseResponse(
        success=True,
        message="Password updated successfully",
        http_status_code=200,
        data=None
    )

@router.delete("", response_model=BaseResponse, status_code=200)
async def delete_user(request: Request, user_service: UserService = Depends(get_user_service)):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    # Logic to delete the user would go here
    # For now, we will just return a success message
    await user_service.delete_user(user_id)

    # Invalidate user session in cache
    session_id = request.cookies.get("session_id")
    await user_service.cache_service.delete(f"session:{session_id}")

    return BaseResponse(
        success=True,
        message="User deleted successfully",
        http_status_code=200,
        data=None
    )