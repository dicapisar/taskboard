import uuid

from fastapi import APIRouter, Depends, Request, HTTPException

from src.app.schemas.base_response import BaseResponse
from src.app.services.task_service import TaskService, get_task_service

router = APIRouter()

@router.get("", response_model=BaseResponse, status_code=200)
async def get_tasks(request: Request, task_service: TaskService = Depends(get_task_service)):

    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    task_list = await task_service.get_tasks(user_id)

    if not task_list:
        raise HTTPException(status_code=404, detail="Task not found")

    tasks_data = {
        "tasks": [task.dict() for task in task_list]
    }

    data_response = BaseResponse(
        success=True,
        message="Tasks retrieved successfully",
        http_status_code=200,
        data=tasks_data
    )
    return data_response