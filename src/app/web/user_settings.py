# Import FastAPI classes for routing, handling requests, and raising exceptions
from fastapi import APIRouter, Request, HTTPException

# Import Jinja2 templating engine to render HTML files dynamically
from fastapi.templating import Jinja2Templates

# Import application settings, including template directory path
from src.app.core.config import settings

# Create a new APIRouter instance to group related routes
router = APIRouter()

# Configure the Jinja2Templates engine with the directory where HTML templates are stored
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)


@router.get("")
async def settings_page(request: Request):
    """
    Render the user settings page.

    This endpoint handles a GET request to the root path of this router.
    It checks if the user is authenticated based on the session data stored in the request.
    If the session is missing, it raises an HTTP 401 Unauthorized error.
    Otherwise, it renders the user settings HTML page with user-specific data.

    :param request: The incoming HTTP request object.
    :return: Rendered HTML template for user settings.
    """

    # Retrieve user session data stored in the request state (middleware-assigned)
    user_data_session = request.state.session

    # If no session exists, raise an Unauthorized HTTP exception
    if not user_data_session:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # Render the 'user_settings.html' page with user session data passed to the template
    return templates.TemplateResponse(
        "user_settings/user_settings.html",  # Path to the HTML file to be rendered
        {"request": request, **user_data_session}  # Template context: includes request + session data
    )