# Import necessary FastAPI modules for routing, request handling, and error management
from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates

# Import application settings to configure the template directory
from src.app.core.config import settings

# Create a router instance to define route endpoints under a specific path
router = APIRouter()

# Initialize the Jinja2 template engine with the template directory specified in settings
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("")
async def main_board_page(request: Request):
    """
    Render the main board page for authenticated users.

    This route handles GET requests to the root path of the board (e.g., '/mainboard').
    It retrieves the user session data from the request state and verifies authentication.
    If authentication fails, a 401 Unauthorized error is raised.

    :param request: The HTTP request object containing session state and other metadata.
    :return: Rendered HTML page using the 'mainboard/mainboard.html' template.
    """

    # Attempt to extract session data associated with the user from the request
    user_data_session = request.state.session

    # If no session is found, raise an unauthorized access exception
    if not user_data_session:
        raise HTTPException(status_code=401, detail="User not authenticated")

    # If authenticated, render the mainboard template and inject session data as context
    return templates.TemplateResponse(
        "mainboard/mainboard.html",           # Path to the Jinja2 template
        {"request": request, **user_data_session}  # Context dictionary including request and session
    )