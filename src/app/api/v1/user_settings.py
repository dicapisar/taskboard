# Import required modules from the Python standard library
import os

# Import FastAPI components for building API endpoints
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Depends

# Import internal modules for user-related operations and response models
from src.app.dtos.user_detail import UserDetail
from src.app.schemas.base_response import BaseResponse
from src.app.schemas.user import UserUpdate, UserPasswordUpdate
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.services.user_service import UserService, get_user_service

# Define the path where profile images will be stored
UPLOAD_PROFILE_IMAGE_DIR = "src/app/static/img/profile_images/"

# Create a router instance for user-related endpoints
router = APIRouter()

# ------------------------------ Upload Profile Image ------------------------------
@router.post("/profile_image", response_model=BaseResponse, status_code=201)
async def upload_profile_image(request: Request, file: UploadFile = File(...)):
    """
    Upload a new profile image for the authenticated user.
    """

    # Get session data from the request
    user_data_session = request.state.session

    # Validate that the user is authenticated
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Check that the uploaded file is an image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")

    # Only PNG format is allowed for profile images
    if not file.filename.endswith('.png'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PNG is allowed.")

    # Check that the file size is less than 5 MB
    if file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the limit of 5 MB.")

    # Get the user ID from the session
    user_id = int(user_data_session["id"])

    # Create the directory path to save the profile image
    user_profile_image_path = f"{UPLOAD_PROFILE_IMAGE_DIR}/{user_id}/"

    # Create the directory if it doesn't exist
    os.makedirs(user_profile_image_path, exist_ok=True)

    # Define the path and file name for the profile image
    file_path = os.path.join(user_profile_image_path, "user.png")

    # Save the uploaded image to the specified location
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return BaseResponse(
        success=True,
        message="Profile image uploaded successfully",
        http_status_code=201,
        data=None
    )

# ------------------------------ Update User Details ------------------------------
@router.post("/user_details", response_model=BaseResponse, status_code=200)
async def update_user_details(
    request: Request,
    user_detail: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    Update the details (username or email) of the authenticated user.
    """

    user_data_session = request.state.session

    # Check if the user is authenticated
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Retrieve current user info from session
    user_name = user_data_session["username"]
    user_email = user_data_session["email"]
    user_id = int(user_data_session["id"])

    # If no changes were made, return an error
    if user_detail.username == user_name and user_detail.email == user_email:
        raise HTTPException(status_code=400, detail="No changes detected in user details")

    # Check if the new username is already in use
    if user_name != user_detail.username:
        user_name_exists = await user_service.is_username_exists(user_detail.username)
        if user_name_exists:
            raise HTTPException(status_code=400, detail="Username already exists")

    # Check if the new email is already in use
    if user_email != user_detail.email:
        user_email_exists = await user_service.is_email_exists(user_detail.email.__str__())
        if user_email_exists:
            raise HTTPException(status_code=400, detail="Email already exists")

    # Update user details in the database
    await user_service.update_user_details(user_detail, user_id)

    # Update session data with new username and email
    user_data_session["username"] = user_detail.username
    user_data_session["email"] = user_detail.email.__str__()
    session_id = request.cookies.get("session_id")

    # Create a new session object to store in cache
    user_detail = UserDetail(
        id=user_data_session["id"],
        username=user_detail.username,
        email=user_detail.email.__str__(),
        is_admin=user_data_session.get("is_admin", False),
    )

    # Update session in cache
    await cache_service.set_user_session_data(session_id, user_detail)

    return BaseResponse(
        success=True,
        message="User details updated successfully",
        http_status_code=200,
        data=None
    )

# ------------------------------ Update User Password ------------------------------
@router.post("/password", response_model=BaseResponse, status_code=200)
async def update_password(
    request: Request,
    user_password_update: UserPasswordUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """
    Update the password for the authenticated user.
    """

    user_data_session = request.state.session

    # Ensure the user is authenticated
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Ensure both old and new passwords are provided
    if not user_password_update.old_password or not user_password_update.new_password:
        raise HTTPException(status_code=400, detail="Old password and new password are required")

    # Prevent the new password from being the same as the old one
    if user_password_update.old_password == user_password_update.new_password:
        raise HTTPException(status_code=400, detail="Old password and new password cannot be the same")

    # Get user ID and perform password update
    user_id = int(user_data_session["id"])
    await user_service.update_user_password(
        user_id,
        user_password_update.old_password,
        user_password_update.new_password
    )

    return BaseResponse(
        success=True,
        message="Password updated successfully",
        http_status_code=200,
        data=None
    )

# ------------------------------ Delete User Account ------------------------------
@router.delete("", response_model=BaseResponse, status_code=200)
async def delete_user(
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    """
    Delete the user account of the authenticated user.
    """

    user_data_session = request.state.session

    # Check if the user is logged in
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the user ID
    user_id = int(user_data_session["id"])

    # Delete the user from the database
    await user_service.delete_user(user_id)

    # Remove session data from cache
    session_id = request.cookies.get("session_id")
    await user_service.cache_service.delete(f"session:{session_id}")

    return BaseResponse(
        success=True,
        message="User deleted successfully",
        http_status_code=200,
        data=None
    )