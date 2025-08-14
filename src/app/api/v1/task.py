from fastapi import APIRouter, Depends, Request

from src.app.dtos.user_detail import UserDetail
from src.app.schemas.base_response import BaseResponse
from src.app.services.task_service import TaskService

router = APIRouter()

@router.get("/", response_model=BaseResponse, status_code=200)
async def get_tasks(request: Request, task_service: TaskService = Depends(TaskService),
                   user_detail: UserDetail = Depends(get_user_detail)):


    data_response = BaseResponse(
        success=True,
        message="Tasks retrieved successfully",
        http_status_code=200,
        data=[]
    )
    return data_response