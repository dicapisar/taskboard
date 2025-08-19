# Importing standard and third-party libraries
import uuid

# Importing FastAPI modules for routing and handling HTTP requests
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

# Importing necessary schemas and services from the application
from src.app.schemas.login import Login
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.services.login_service import LoginService, get_login_service
from src.app.schemas.base_response import BaseResponse

# Creating an instance of APIRouter to define login-related routes
router = APIRouter()

# Defining a POST route for user login
@router.post("", response_model=BaseResponse, status_code=200)
async def login(
    response: Response,
    payload: Login,
    cache_service: CacheService = Depends(get_cache_service),
    login_service: LoginService = Depends(get_login_service)
):
    """
    This function handles user login requests.
    It verifies the provided credentials and creates a session if successful.
    """

    # Authenticate the user using email and password
    user = await login_service.authenticate_user(payload.email.__str__(), payload.password)

    # If user credentials are incorrect, return an unauthorized error
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Generate a unique session ID to identify the user's session
    session_id = str(uuid.uuid4())

    # Save the user's session data in the Redis cache for later use
    await cache_service.set_user_session_data(session_id, user.to_user_detail())

    # Set a secure HTTP-only cookie in the user's browser with the session ID
    response.set_cookie("session_id", session_id, max_age=3600, httponly=True)

    # Prepare and return a response with user session and profile details
    data_response = BaseResponse(
        success=True,
        message="Login successful",
        http_status_code=200,
        data={
            "session_id": session_id,
            "user_id": user.id,
            "user_name": user.username,
            "email": user.email,
            "is_admin": user.is_admin(),
        }
    )

    return data_response