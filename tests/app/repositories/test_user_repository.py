import pytest
from src.app.repositories.user_repository import UserRepository
from src.app.models.user import User
from src.app.schemas.user import UserCreate, UserUpdate
import bcrypt


@pytest.fixture
def fake_db():
    class FakeSession:
        def __init__(self):
            self.users = [
                User(id=1, username="user1", email="u1@example.com", password=bcrypt.hashpw("123".encode(), bcrypt.gensalt()).decode())
            ]

        def query(self, model):
            class Query:
                def __init__(self, data):
                    self.data = data

                def filter(self, *args):
                    self.filtered = [u for u in self.data if eval(str(args[0]))]
                    return self

                def all(self): return self.filtered
                def first(self): return self.filtered[0] if self.filtered else None
                def count(self): return len(self.filtered)

            return Query(self.users)

        def add(self, obj):
            obj.id = 2
            self.users.append(obj)

        def commit(self): pass
        def refresh(self, obj): pass
        def delete(self, obj): self.users.remove(obj)

    return FakeSession()


@pytest.mark.asyncio
async def test_get_by_email(fake_db):
    repo = UserRepository(db=fake_db)
    user = await repo.get_by_email("u1@example.com")
    assert user.username == "user1"


@pytest.mark.asyncio
async def test_get_by_id(fake_db):
    repo = UserRepository(db=fake_db)
    user = await repo.get_by_id(1)
    assert user.email == "u1@example.com"


@pytest.mark.asyncio
async def test_create_user(fake_db):
    repo = UserRepository(db=fake_db)
    payload = UserCreate(username="new", email="new@example.com", password="secret")
    user = await repo.create_user(payload)
    assert user.username == "new"
    assert user.password != "secret"  # debe estar hasheado


@pytest.mark.asyncio
async def test_update_user_details(fake_db):
    repo = UserRepository(db=fake_db)
    payload = UserUpdate(username="updated", email="updated@example.com")
    await repo.update_user_details(1, payload)
    assert fake_db.users[0].username == "updated"


@pytest.mark.asyncio
async def test_update_user_password(fake_db):
    repo = UserRepository(db=fake_db)
    old_hash = fake_db.users[0].password
    await repo.update_user_password(1, "123", "newpass")
    assert fake_db.users[0].password != old_hash


@pytest.mark.asyncio
async def test_delete_user(fake_db):
    repo = UserRepository(db=fake_db)
    await repo.delete_user(1)
    assert not any(u.id == 1 for u in fake_db.users)


@pytest.mark.asyncio
async def test_list_users(fake_db):
    repo = UserRepository(db=fake_db)
    result = await repo.list_users()
    assert len(result["users"]) == 1


@pytest.mark.asyncio
async def test_is_username_exists(fake_db):
    repo = UserRepository(db=fake_db)
    assert await repo.is_username_exists("user1") is True
    assert await repo.is_username_exists("none") is False


@pytest.mark.asyncio
async def test_is_email_exists(fake_db):
    repo = UserRepository(db=fake_db)
    assert await repo.is_email_exists("u1@example.com") is True
    assert await repo.is_email_exists("no@x.com") is False
