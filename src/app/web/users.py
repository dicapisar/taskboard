# Import necessary modules and classes from FastAPI, SQLAlchemy, and the application
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

# Import the function to get the database session
from src.app.core.database import get_db

# Import the service layer that handles user-related business logic
from src.app.services.user_service import UserService

# Import application settings to access the templates directory path
from src.app.core.config import settings

# Create a new APIRouter instance to define routes related to user pages
router = APIRouter()

# Set up the Jinja2 template engine with the specified template directory
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("")
async def users_page(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Render the page that displays a list of all users.

    This endpoint handles a GET request to the users route.
    It initializes the UserService with a database session and retrieves all users.
    Then, it renders the HTML template for displaying the list.

    :param request: The incoming HTTP request object.
    :param db: Asynchronous database session provided via dependency injection.
    :return: Rendered HTML page with the list of users.
    """

    # Create an instance of the UserService using the database session
    service = UserService(db)

    # Fetch the list of users from the service
    users = await service.list_users()

    # Render the 'list.html' template inside the 'users' folder
    # The context includes the request and the list of users
    return templates.TemplateResponse(
        "users/list.html",
        {"request": request, "users": users}
    )