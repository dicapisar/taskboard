import json

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from src.app.api.v1 import users as api_users
from src.app.api.v1 import login as api_login
from src.app.api.v1 import task as api_task
from src.app.api.v1 import user_settings as api_user_settings
from src.app.api.v1 import logout as api_logout
from src.app.web import login as web_login
from src.app.web import main_board as web_main_board
from src.app.web import user_settings as web_user_settings
from src.app.core.config import settings
from src.app.core.database import engine, Base
from src.app.core.cache import redis

app = FastAPI(title=settings.PROJECT_NAME)

# Middleware
@app.middleware("http")
async def add_session_middleware(request: Request, call_next):

    url_exceptions = [
        "/login",
        "/static",
        "/docs",
        "/redoc",
        "/forgot_password",
        "/api/v1/login",
        "/api/v1/users"
    ]

    # Check if the request URL is in the exceptions list or starts with the static files path

    if request.url.path.startswith("/static/"):
        return await call_next(request)

    if request.url.path in url_exceptions:
        return await call_next(request)

    session_id = request.cookies.get("session_id")
    if not session_id:
        return RedirectResponse(url="/login")

    session_key = f"session:{session_id}"
    session_data = await redis.get(session_key)

    if not session_data:
        return RedirectResponse(url="/login")

    try:
        request.state.session = json.loads(session_data)
    except json.JSONDecodeError:
        return RedirectResponse(url="/login")

    response = await call_next(request)
    return response

# Web Routes
app.include_router(web_main_board.router, prefix="/main", tags=["Web - Login"])
#app.include_router(web_users.router, prefix="/users", tags=["Web - Users"])
app.include_router(web_login.router, prefix="/login", tags=["Web - Login"])
app.include_router(web_user_settings.router, prefix="/settings", tags=["Web - User Settings"])

# API Routes
app.include_router(api_login.router, prefix="/api/v1/login", tags=["API - Login"])
app.include_router(api_users.router, prefix="/api/v1/users", tags=["API - Users"])
app.include_router(api_task.router, prefix="/api/v1/tasks", tags=["API - Tasks"])
app.include_router(api_user_settings.router, prefix="/api/v1/user_settings", tags=["API - User Settings"])
app.include_router(api_logout.router, prefix="/api/v1/logout", tags=["API - Logout"])


# Static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

@app.on_event("startup")
async def on_startup():
    # Crear tablas (en producción usar migraciones)
    import src.app.models.role
    import src.app.models.user
    import src.app.models.task

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)