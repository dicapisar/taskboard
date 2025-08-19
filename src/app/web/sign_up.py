# Import FastAPI components to handle routing and incoming requests
from fastapi import APIRouter, Request

# Import the Jinja2 template engine to render HTML templates
from fastapi.templating import Jinja2Templates

# Import application configuration, including the path to the templates directory
from src.app.core.config import settings

# Create a new APIRouter instance to define route handlers under a shared path prefix
router = APIRouter()

# Initialize Jinja2Templates with the path to the HTML template directory
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("")
async def sign_up_page(request: Request):
    """
    Render the sign-up page.

    This function handles GET requests to the root of this router.
    It returns an HTML template for the user registration form.

    :param request: The HTTP request object (required by Jinja2 templates).
    :return: Rendered HTML page using the sign_up/sign_up.html template.
    """
    return templates.TemplateResponse(
        "sign_up/sign_up.html",  # Path to the HTML file to render
        {"request": request}     # Context dictionary passed to the template
    )