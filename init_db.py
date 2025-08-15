# init_db.py
import asyncio
import os
import bcrypt
from sqlalchemy import select, func

from src.app.core.database import engine, SessionLocal
from src.app.core.database import Base

# 🔴 IMPORTA TODOS LOS MODELOS ANTES DE USARLOS (registro en el mapper)
import src.app.models.role   # noqa: F401
import src.app.models.user   # noqa: F401
import src.app.models.task   # noqa: F401

from src.app.models.role import Role
from src.app.models.user import User


async def init_db():
    # Crea TODAS las tablas conocidas por el Base (requiere que los modelos estén importados)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        # ¿Ya hay roles? (si hay, asumimos que ya se hizo el seeding)
        roles_count = (
            await session.execute(select(func.count()).select_from(Role))
        ).scalar_one()

        if roles_count and roles_count > 0:
            print("🔹 Roles already exist, skipping initialization.")
            return

        # Crea roles
        admin_role = Role(id=1, name="admin", description="System administrator")
        student_role = Role(id=2, name="student", description="Student")
        session.add_all([admin_role, student_role])
        await session.commit()
        print("✅ Roles created.")

        # Credenciales admin desde entorno
        username = os.getenv("ADMIN_USERNAME", "admin")
        email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        password = os.getenv("ADMIN_PASSWORD", "admin123")

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode()

        # Evita duplicados por si existe el usuario
        existing_admin = (
            await session.execute(select(User).where(User.username == username))
        ).scalar_one_or_none()

        if not existing_admin:
            admin_user = User(
                id=1,
                username=username,
                email=email,
                password=hashed_pw,
                is_active=True,
                role_id=1,
            )
            session.add(admin_user)
            await session.commit()
            print("✅ Admin user created.")
        else:
            print("🔹 Admin user already exists, skipping.")

if __name__ == "__main__":
    asyncio.run(init_db())