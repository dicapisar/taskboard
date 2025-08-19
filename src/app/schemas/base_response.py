# Import the base model class from Pydantic
from pydantic import BaseModel

# ---------------------------- Response Schema ----------------------------

class BaseResponse(BaseModel):
    """
    This model defines a standard response format used across the application.
    It includes a message, a success flag, an HTTP status code, and optional data.
    """

    message: str              # A short message describing the result (e.g., "Task created successfully")
    success: bool             # Indicates whether the operation was successful or not
    http_status_code: int     # The HTTP status code related to the response (e.g., 200, 404, 500)
    data: dict | None         # Optional dictionary containing any data returned to the client

    class Config:
        from_attributes = True  # Enable ORM compatibility to convert from database models