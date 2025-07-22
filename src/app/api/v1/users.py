from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.database import get_db
from src.app.schemas.user import UserCreate, UserOut
from src.app.services.user_service import UserService

router = APIRouter()

@router.post("/", response_model=UserOut, status_code=201)
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    existing = await service.repo.get_by_username(payload.username)
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    existing_email = await service.repo.get_by_email(payload.email)
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already exists")
    user = await service.create_user(payload)
    return user

@router.get("/", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    users = await service.list_users()
    return users