# Import standard and third-party libraries
import json
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Import API route modules
from src.app.api.v1 import users as api_users
from src.app.api.v1 import login as api_login
from src.app.api.v1 import task as api_task
from src.app.api.v1 import user_settings as api_user_settings
from src.app.api.v1 import logout as api_logout

# Import Web route modules
from src.app.web import login as web_login
from src.app.web import main_board as web_main_board
from src.app.web import user_settings as web_user_settings
from src.app.web import sign_up as web_sign_up

# Import configuration and infrastructure modules
from src.app.core.config import settings
from src.app.core.database import engine, Base
from src.app.core.cache import redis

# Initialize the FastAPI app with the project name from settings
app = FastAPI(title=settings.PROJECT_NAME)

# -------------------------------
# Middleware for session handling
# -------------------------------
@app.middleware("http")
async def add_session_middleware(request: Request, call_next):
    """
    Custom middleware that handles session validation using Redis.
    Redirects unauthenticated users to the login page if needed.
    """

    # Redirect root path "/" to "/main"
    if request.url.path == "/":
        return RedirectResponse(url="/main")

    # List of paths that are allowed without session validation
    url_exceptions = [
        "/login",
        "/static",
        "/docs",
        "/redoc",
        "/forgot_password",
        "/api/v1/login",
        "/api/v1/users",
        "/sign_up",
    ]

    # Allow access to static resources without authentication
    if request.url.path.startswith("/static/"):
        return await call_next(request)

    # Allow access to explicitly whitelisted paths
    if request.url.path in url_exceptions:
        return await call_next(request)

    # Get the session ID from browser cookies
    session_id = request.cookies.get("session_id")
    if not session_id:
        return RedirectResponse(url="/login")

    # Compose the Redis session key
    session_key = f"session:{session_id}"

    # Retrieve session data from Redis cache
    session_data = await redis.get(session_key)

    if not session_data:
        return RedirectResponse(url="/login")

    # Attempt to decode the session JSON string into a dictionary
    try:
        request.state.session = json.loads(session_data)
    except json.JSONDecodeError:
        return RedirectResponse(url="/login")

    # Continue with the request
    response = await call_next(request)
    return response

# -------------------------------
# Web Routes (HTML views)
# -------------------------------
app.include_router(web_main_board.router, prefix="/main", tags=["Web - Login"])
app.include_router(web_login.router, prefix="/login", tags=["Web - Login"])
app.include_router(web_user_settings.router, prefix="/settings", tags=["Web - User Settings"])
app.include_router(web_sign_up.router, prefix="/sign_up", tags=["Web - Sign Up"])
# Note: web_users route is commented out

# -------------------------------
# API Routes (JSON endpoints)
# -------------------------------
app.include_router(api_login.router, prefix="/api/v1/login", tags=["API - Login"])
app.include_router(api_users.router, prefix="/api/v1/users", tags=["API - Users"])
app.include_router(api_task.router, prefix="/api/v1/tasks", tags=["API - Tasks"])
app.include_router(api_user_settings.router, prefix="/api/v1/user_settings", tags=["API - User Settings"])
app.include_router(api_logout.router, prefix="/api/v1/logout", tags=["API - Logout"])

# -------------------------------
# Static Files Configuration
# -------------------------------
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

# -------------------------------
# Startup Event: Database Tables
# -------------------------------
@app.on_event("startup")
async def on_startup():
    """
    Runs when the application starts.
    It creates the database tables if they do not exist.
    NOTE: In production, migrations should be used instead of auto-create.
    """
    # Import models to register them with SQLAlchemy's metadata
    import src.app.models.role
    import src.app.models.user
    import src.app.models.task

    # Use an asynchronous connection to create the tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)