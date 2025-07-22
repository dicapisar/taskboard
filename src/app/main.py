from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.app.api.v1 import users as api_users
from src.app.web import users as web_users
from src.app.core.config import settings
from src.app.core.database import engine, Base

app = FastAPI(title=settings.PROJECT_NAME)

# Rutas
app.include_router(api_users.router, prefix="/api/v1/users", tags=["API - Users"])
app.include_router(web_users.router, prefix="/web/users", tags=["Web - Users"])

# Static files
app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

@app.on_event("startup")
async def on_startup():
    # Crear tablas (en producción usar migraciones)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)