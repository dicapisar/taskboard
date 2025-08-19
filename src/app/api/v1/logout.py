# Importing the UUID module for working with unique identifiers
import uuid

# Importing necessary FastAPI components for routing and request handling
from fastapi import APIRouter, Depends, HTTPException, Request

# Importing the cache service and the standardized response schema
from src.app.services.cache_service import CacheService, get_cache_service
from src.app.schemas.base_response import BaseResponse

# Creating a new API router for handling login-related endpoints
router = APIRouter()

# Defining a POST endpoint to log out a user by clearing session data
@router.post("", response_model=BaseResponse, status_code=200)
async def login(
    request: Request,
    cache_service: CacheService = Depends(get_cache_service)
):
    """
    This function logs out a user by deleting the session from the cache.
    It checks if the user is authenticated before performing the logout.
    """

    # Retrieve the user's session data from the request state
    user_data_session = request.state.session

    # Validate that the session exists and contains a valid user ID
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Get the session ID from the user's cookies
    session_id = request.cookies.get("session_id")

    # Remove the session data from the cache storage (e.g., Redis)
    await cache_service.delete(f"session:{session_id}")

    # Prepare a response indicating the logout was successful
    data_response = BaseResponse(
        success=True,
        message="Login successful",
        http_status_code=200,
        data=None
    )

    return data_response