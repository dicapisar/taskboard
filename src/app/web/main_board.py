from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from src.app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("")
async def main_board_page(request: Request):

    return templates.TemplateResponse(
        "mainboard/mainboard.html",
        {"request": request}
    )