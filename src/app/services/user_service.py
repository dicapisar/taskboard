from src.app.repositories.user_repository import UserRepository
from src.app.schemas.user import UserCreate
from src.app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.cache import redis
import json

CACHE_KEY_ALL_USERS = "users:all"
CACHE_TTL_SECONDS = 60

class UserService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def create_user(self, data: UserCreate):
        # invalidar cache antes o después de commit

        user_model = User(**data.model_dump())
        user_model.role_id = 2
        user_model.is_active = True

        user = await self.repo.create(user_model)
        await redis.delete(CACHE_KEY_ALL_USERS)
        return user

    async def list_users(self):
        cached = await redis.get(CACHE_KEY_ALL_USERS)
        if cached:
            # Deserializa el JSON completo y devuelve la lista de dicts
            return json.loads(cached)

        users = await self.repo.list_all()
        serializable = [
            {"id": u.id, "username": u.username, "email": u.email}
            for u in users
        ]
        await redis.set(
            CACHE_KEY_ALL_USERS,
            json.dumps(serializable),
            ex=CACHE_TTL_SECONDS
        )
        return serializable