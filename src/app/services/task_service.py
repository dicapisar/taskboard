from typing import List

from src.app.dtos.user_detail import UserDetail
from src.app.repositories.task_repository import TaskRepository, get_task_repository
from fastapi import Depends

from src.app.schemas.task import TaskOut, TaskCreate, TaskUpdate, TaskStatusEnum


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def get_tasks(self, owner_id: int) -> List[TaskOut]:
        """
        Retrieve all tasks for a given user.

        :param owner_id: ID of the user whose tasks are to be retrieved.
        :return: List of TaskOut objects representing the user's tasks.
        """

        if not owner_id:
            raise ValueError("User id is required .")

        if not isinstance(owner_id, int):
            raise TypeError("User ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Fetch all tasks for the user
        return await self.task_repository.get_all_tasks_by_user_id(owner_id)

    async def get_task_by_id(self, task_id: int, owner_id: int) -> TaskOut | None:
        """
        Retrieve a specific task by its ID for a given user.

        :param task_id: ID of the task to retrieve.
        :param owner_id: ID of the user who owns the task.
        :return: TaskOut object representing the task, or None if not found.
        """

        if not owner_id :
            raise ValueError("Owner id is required.")

        if not isinstance(task_id, int):
            raise TypeError("Task ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Fetch the task by ID for the user
        return await self.task_repository.get_task_by_id_and_user_id(task_id, owner_id)

    async def create_task(self, task_data: TaskCreate, owner_id: int) -> TaskOut:
        """
        Create a new task for a given user.

        :param task_data: TaskCreate object containing task details.
        :param owner_id: UserDetail object containing user information.
        :return: TaskOut object representing the created task.
        """

        if not owner_id:
            raise ValueError("Owner id is required.")

        if not isinstance(owner_id, int):
            raise TypeError("Owner ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Create the task for the user
        return await self.task_repository.create_task(task_data, owner_id)

    async def update_task(self, task_data: TaskUpdate, owner_id: int) -> TaskOut:
        """
        Update an existing task for a given user.

        :param task_data: TaskUpdate object containing updated task details.
        :param owner_id: ID of the user who owns the task.
        :return: TaskOut object representing the updated task.
        """

        if not owner_id:
            raise ValueError("Owner ID is required.")

        if not isinstance(owner_id, int):
            raise TypeError("Owner ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Check if the task ID is provided in the task_data
        if not task_data.id:
            raise ValueError("Task ID is required for updating a task.")

        if not self.task_repository.get_task_by_id_and_user_id(task_data.id, owner_id):
            raise ValueError(f"Task with ID {task_data.id} not found for user {owner_id}.")

        # Update the task for the user
        return await self.task_repository.update_task(task_data.id, task_data)


    async def update_task_status(self, task_id: int, status: TaskStatusEnum, owner_id: int) -> TaskOut:
        """
        Update the status of an existing task for a given user.

        :param task_id: ID of the task to update.
        :param status: New status for the task.
        :param owner_id: ID of the user who owns the task.
        :return: TaskOut object representing the updated task.
        """

        if not owner_id:
            raise ValueError("Owner ID is required.")

        if not isinstance(owner_id, int):
            raise TypeError("Owner ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        # Check if the task exists
        task = await self.task_repository.get_task_by_id_and_user_id(task_id, owner_id)
        if not task:
            raise ValueError(f"Task with ID {task_id} not found for user {owner_id}.")

        task_update = TaskUpdate(
            id=task_id,
            title=task.title,
            description=task.description,
            completed=task.completed,
            priority=task.priority,
            status=status,  # Update the status
            due_date=task.due_date,
            subject=task.subject
        )

        # Update the task status
        return await self.update_task(task_update, owner_id)


    async def delete_task(self, task_id: int, owner_id: int) -> bool:
        """
        Delete a task by its ID.

        :param task_id: ID of the task to delete.
        :param owner_id: ID of the task to delete.
        :return: True if the task was deleted successfully, False otherwise.
        """

        if not isinstance(task_id, int):
            raise TypeError("Task ID must be an integer.")

        # Check if the task repository is initialized
        if not self.task_repository:
            raise ValueError("Task repository is not initialized.")

        task = await self.task_repository.get_task_by_id_and_user_id(task_id, owner_id)

        # Check if the task exists before attempting to delete
        if not task:
            raise ValueError(f"Task with ID {task_id} not found.")

        if task.owner_id != owner_id:
            raise ValueError(f"User {owner_id} does not have permission to delete task {task_id}.")

        # Delete the task by ID
        return await self.task_repository.delete_task_(task_id)

async def get_task_service(task_repository: TaskRepository = Depends(get_task_repository)):
    """
    Dependency injection for TaskService.

    :param task_repository: TaskRepository instance.
    :return: TaskService instance.
    """
    return TaskService(task_repository=task_repository)