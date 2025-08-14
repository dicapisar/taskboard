import json

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from src.app.api.v1 import users as api_users
from src.app.api.v1 import login as api_login
from src.app.web import users as web_users
from src.app.web import login as web_login
from src.app.web import main_board as web_main_board
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

# API Routes
app.include_router(api_users.router, prefix="/api/v1/users", tags=["API - Users"])
app.include_router(api_login.router, prefix="/api/v1/login", tags=["API - Login"])

# Web Routes
app.include_router(web_users.router, prefix="/users", tags=["Web - Users"])

app.include_router(web_login.router, prefix="/login", tags=["Web - Login"])

app.include_router(web_main_board.router, prefix="/login", tags=["Web - Login"])
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