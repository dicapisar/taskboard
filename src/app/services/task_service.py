from typing import List

from src.app.dtos.user_detail import UserDetail
from src.app.repositories.task_repository import TaskRepository, get_task_repository
from fastapi import Depends

from src.app.schemas.task import TaskOut, TaskCreate, TaskUpdate


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def get_tasks(self, user_id: int) -> List[TaskOut]:
        """
        Retrieve all tasks for a given user.

        :param user_detail: UserDetail object containing user information.
        :return: List of TaskOut objects representing the user's tasks.
        """

        if not user_id:
            raise ValueError("User id is required .")

        if not isinstance(user_id, int):
            raise TypeError("User ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Fetch all tasks for the user
        return await self.task_repository.get_all_tasks_by_user_id(user_id)

    async def get_task_by_id(self, task_id: int, user_detail: UserDetail) -> TaskOut | None:
        """
        Retrieve a specific task by its ID for a given user.

        :param task_id: ID of the task to retrieve.
        :param user_detail: UserDetail object containing user information.
        :return: TaskOut object representing the task, or None if not found.
        """

        if not user_detail or not user_detail.id:
            raise ValueError("User detail is required and must contain a valid user ID.")

        if not isinstance(task_id, int):
            raise TypeError("Task ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Fetch the task by ID for the user
        return await self.task_repository.get_task_by_id_and_user_id(task_id, user_detail.id)

    async def create_task(self, task_data: TaskCreate, user_detail: UserDetail) -> TaskOut:
        """
        Create a new task for a given user.

        :param task_data: TaskCreate object containing task details.
        :param user_detail: UserDetail object containing user information.
        :return: TaskOut object representing the created task.
        """

        if not user_detail or not user_detail.id:
            raise ValueError("User detail is required and must contain a valid user ID.")

        if not isinstance(user_detail.id, int):
            raise TypeError("User ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Validate task data
        if not task_data.owner_id == user_detail.id:
            raise ValueError("Task owner ID must match the user ID.")

        # Create the task for the user
        return await self.task_repository.create_task(task_data, user_detail.id)

    async def update_task(self, task_data: TaskUpdate, user_detail: UserDetail) -> TaskOut:
        """
        Update an existing task for a given user.

        :param task_data: TaskUpdate object containing updated task details.
        :param user_detail: UserDetail object containing user information.
        :return: TaskOut object representing the updated task.
        """

        if not user_detail or not user_detail.id:
            raise ValueError("User detail is required and must contain a valid user ID.")

        if not isinstance(user_detail.id, int):
            raise TypeError("User ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Check if the task ID is provided in the task_data
        if not task_data.id:
            raise ValueError("Task ID is required for updating a task.")

        if not self.task_repository.get_task_by_id_and_user_id(task_data.id, user_detail.id):
            raise ValueError(f"Task with ID {task_data.id} not found for user {user_detail.id}.")

        # Update the task for the user
        return await self.task_repository.update_task(task_data.id, task_data)

    async def delete_task(self, task_id: int, user_detail: UserDetail) -> bool:
        """
        Delete a task by its ID.

        :param task_id: ID of the task to delete.
        :return: True if the task was deleted successfully, False otherwise.
        """

        if not isinstance(task_id, int):
            raise TypeError("Task ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        task = await self.task_repository.get_task_by_id_and_user_id(task_id, user_detail.id)

        # Check if the task exists before attempting to delete
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        if task.owner_id != user_detail.id:
            raise ValueError(f"User {user_detail.id} does not have permission to delete task {task_id}.")

        # Delete the task by ID
        return await self.task_repository.delete_task_(task_id)

async def get_task_service(task_repository: TaskRepository = Depends(get_task_repository)):
    """
    Dependency injection for TaskService.

    :param task_repository: TaskRepository instance.
    :return: TaskService instance.
    """
    return TaskService(task_repository=task_repository)