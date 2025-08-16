from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from src.app.core.config import settings

router = APIRouter()
templates = Jinja2Templates(directory=settings.TEMPLATE_DIR)

@router.get("")
async def settings_page(request: Request):
    user_data_session = request.state.session

    if not user_data_session:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return templates.TemplateResponse(
        "user_settings/user_settings.html",
        {"request": request, **user_data_session}
    )