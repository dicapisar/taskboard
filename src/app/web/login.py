# Import necessary modules for routing and template rendering
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.app.core.config import settings

# Create a new router instance for defining route endpoints
router = APIRouter()

# Set up Jinja2 template engine using the configured template directory
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("")
async def login_page(request: Request):
    """
    Render the login HTML page.

    This endpoint handles GET requests to the root path ("") and returns the login page.
    It passes the `request` object to the template, which is required by FastAPI's Jinja2 integration.

    :param request: The HTTP request object from the client.
    :return: HTML response rendered from 'login/login.html' template.
    """
    return templates.TemplateResponse(
        "login/login.html",  # Path to the login template
        {"request": request}  # Context needed by the template engine
    )