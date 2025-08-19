# Import FastAPI tools for API routing and exception handling
from fastapi import APIRouter, Depends, HTTPException

# Import application schemas and services
from src.app.schemas.base_response import BaseResponse
from src.app.schemas.user import UserCreate, UserOut
from src.app.services.user_service import UserService, get_user_service

# Initialize a router for user-related endpoints
router = APIRouter()

# ---------------------------- Create User Endpoint ----------------------------
@router.post("", response_model=BaseResponse, status_code=201)
async def create_user(payload: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    Create a new user account.
    This function checks for duplicate usernames and emails before creating the user.
    """

    # Check if the username already exists
    existing = await user_service.is_username_exists(payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")

    # Check if the email already exists
    existing_email = await user_service.is_email_exists(payload.email.__str__())
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exists")

    # If both username and email are unique, create the user
    user = await user_service.create_user(payload)

    # Prepare response data with new user's information
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

# ---------------------------- List Users Endpoint ----------------------------
@router.get("", response_model=BaseResponse, status_code=200)
async def list_users(user_service: UserService = Depends(get_user_service)):
    """
    Retrieve a list of all users.
    This endpoint returns user data for administrative or management purposes.
    """

    # Fetch the list of users from the user service
    users = await user_service.list_users()

    # If no users are found, raise a 404 error
    if users is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the list of users in the response
    data_response = BaseResponse(
        success=True,
        message="Users retrieved successfully",
        http_status_code=200,
        data=users
    )
    return data_response