# Import standard libraries
import json
import uuid

# Import FastAPI modules for API routing and handling HTTP requests
from fastapi import APIRouter, Depends, Request, HTTPException, Path

# Import application-specific schemas and services
from src.app.schemas.base_response import BaseResponse
from src.app.schemas.task import TaskCreate, TaskChangeStatus, TaskUpdate
from src.app.services.task_service import TaskService, get_task_service

# Initialize an API router for task-related operations
router = APIRouter()

# Endpoint to retrieve all tasks for an authenticated user
@router.get("", response_model=BaseResponse, status_code=200)
async def get_tasks(request: Request, task_service: TaskService = Depends(get_task_service)):
    """
    This endpoint returns all tasks that belong to the authenticated user.
    """

    # Get user session from the request
    user_data_session = request.state.session

    # Check if the user is authenticated
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Extract user ID from session data
    user_id = int(user_data_session["id"])

    # Call the service to get all tasks for this user
    task_list = await task_service.get_tasks(user_id)

    # If no tasks found, return a 404 error
    if not task_list:
        raise HTTPException(status_code=404, detail="Task not found")

    # Prepare task data for the response
    tasks_data = {
        "tasks": [task.model_dump() for task in task_list],
        "total_tasks": len(task_list)
    }

    # Send a successful response with the list of tasks
    data_response = BaseResponse(
        success=True,
        message="Tasks retrieved successfully",
        http_status_code=200,
        data=tasks_data
    )
    return data_response


# Endpoint to create a new task
@router.post("", response_model=BaseResponse, status_code=201)
async def create_task(request: Request, task_data: TaskCreate, task_service: TaskService = Depends(get_task_service)):
    """
    This endpoint creates a new task for the authenticated user.
    """

    # Get user session from the request
    user_data_session = request.state.session

    # Validate user authentication
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Extract user ID
    user_id = int(user_data_session["id"])

    # Call the service to create the task
    task_created = await task_service.create_task(task_data, user_id)

    # Return a success response with the task data
    data_response = BaseResponse(
        success=True,
        message="Task created successfully",
        http_status_code=201,
        data=task_created.model_dump()
    )
    return data_response


# Endpoint to update the status of a specific task
@router.patch("/{task_id}", response_model=BaseResponse, status_code=200)
async def update_task_status(
    request: Request,
    task_status: TaskChangeStatus,
    task_service: TaskService = Depends(get_task_service),
    task_id: int = Path(..., description="task ID")
):
    """
    This endpoint updates the status of a given task for the authenticated user.
    """

    # Get user session from the request
    user_data_session = request.state.session

    # Ensure the user is logged in
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    # Call the service to update the task status
    updated_task = await task_service.update_task_status(task_id, task_status.status, user_id)

    # If task is not found, raise 404 error
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the updated task
    data_response = BaseResponse(
        success=True,
        message="Task updated successfully",
        http_status_code=200,
        data=updated_task.model_dump()
    )
    return data_response


# Endpoint to get a specific task by its ID
@router.get("/{task_id}", response_model=BaseResponse, status_code=200)
async def get_task_by_id(
    request: Request,
    task_service: TaskService = Depends(get_task_service),
    task_id: int = Path(..., description="task ID")
):
    """
    This endpoint returns a single task by its ID, if the user owns it.
    """

    user_data_session = request.state.session

    # Check authentication
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    # Get the task using the service
    task = await task_service.get_task_by_id(task_id, user_id)

    # If task does not exist, return 404
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Return the task data
    data_response = BaseResponse(
        success=True,
        message="Task retrieved successfully",
        http_status_code=200,
        data=task.model_dump()
    )
    return data_response


# Endpoint to update an existing task's content (not only status)
@router.post("/{task_id}", response_model=BaseResponse, status_code=200)
async def update_task(
    request: Request,
    task_data: TaskUpdate,
    task_service: TaskService = Depends(get_task_service),
    task_id: int = Path(..., description="task ID")
):
    """
    This endpoint updates all the details of a task for the authenticated user.
    """

    user_data_session = request.state.session

    # Check for valid authentication
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    # Set the task ID in the update object
    task_data.id = task_id

    # Update the task using the service
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


# Endpoint to delete a task by its ID
@router.delete("/{task_id}", response_model=BaseResponse, status_code=200)
async def delete_task(
    request: Request,
    task_service: TaskService = Depends(get_task_service),
    task_id: int = Path(..., description="task ID")
):
    """
    This endpoint deletes a task that belongs to the authenticated user.
    """

    user_data_session = request.state.session

    # Confirm user identity
    if not user_data_session or not user_data_session["id"] or not isinstance(user_data_session["id"], int):
        raise HTTPException(status_code=401, detail="User not authenticated")

    user_id = int(user_data_session["id"])

    # Attempt to delete the task
    deleted = await task_service.delete_task(task_id, user_id)

    # If task is not found or deletion fails
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")

    data_response = BaseResponse(
        success=True,
        message="Task deleted successfully",
        http_status_code=200,
        data=None
    )
    return data_response