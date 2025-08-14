import json
import uuid

from fastapi import APIRouter, Depends, Request, HTTPException, Path

from src.app.schemas.base_response import BaseResponse
from src.app.schemas.task import TaskCreate, TaskChangeStatus, TaskUpdate
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
        "tasks": [task.model_dump() for task in task_list],
        "total_tasks": len(task_list)
    }

    data_response = BaseResponse(
        success=True,
        message="Tasks retrieved successfully",
        http_status_code=200,
        data=tasks_data
    )
    return data_response

@router.post("", response_model=BaseResponse, status_code=201)
async def create_task(request: Request, task_data: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    task_created = await task_service.create_task(task_data, user_id)

    data_response = BaseResponse(
        success=True,
        message="Task created successfully",
        http_status_code=201,
        data=task_created.model_dump()
    )
    return data_response

@router.patch("/{task_id}", response_model=BaseResponse, status_code=200)
async def update_task_status(request: Request, task_status: TaskChangeStatus, task_service: TaskService = Depends(get_task_service), task_id: int = Path(..., description= "task ID")):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    updated_task = await task_service.update_task_status(task_id, task_status.status, user_id)

    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")

    data_response = BaseResponse(
        success=True,
        message="Task updated successfully",
        http_status_code=200,
        data=updated_task.model_dump()
    )
    return data_response

@router.get("/{task_id}", response_model=BaseResponse, status_code=200)
async def get_task_by_id(request: Request, task_service: TaskService = Depends(get_task_service), task_id: int = Path(..., description="task ID")):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    task = await task_service.get_task_by_id(task_id, user_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    data_response = BaseResponse(
        success=True,
        message="Task retrieved successfully",
        http_status_code=200,
        data=task.model_dump()
    )
    return data_response

@router.post("/{task_id}", response_model=BaseResponse, status_code=200)
async def update_task(request: Request, task_data: TaskUpdate, task_service: TaskService = Depends(get_task_service), task_id: int = Path(..., description="task ID")):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    task_data.id = task_id

    updated_task = await task_service.update_task(task_data, user_id)

    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")

    data_response = BaseResponse(
        success=True,
        message="Task updated successfully",
        http_status_code=200,
        data=updated_task.model_dump()
    )
    return data_response

@router.delete("/{task_id}", response_model=BaseResponse, status_code=200)
async def delete_task(request: Request, task_service: TaskService = Depends(get_task_service), task_id: int = Path(..., description="task ID")):
    user_data_session = request.state.session

    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    deleted = await task_service.delete_task(task_id, user_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    data_response = BaseResponse(
        success=True,
        message="Task deleted successfully",
        http_status_code=200,
        data=None
    )
    return data_response