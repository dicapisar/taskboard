from pydantic import BaseModel

class BaseResponse(BaseModel):
    message: str
    success: bool
    http_status_code: int
    data: dict | None

    class Config:
        from_attributes = True  # Pydantic v2