from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import get_db
from src.app.services.user_service import UserService
from src.app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("/")
async def users_page(request: Request, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    users = await service.list_users()
    return templates.TemplateResponse(
        "users/list.html",
        {"request": request, "users": users}
    )