import pytest
from src.app.repositories.cache_repository import CacheRepository
from src.app.dtos.user_detail import UserDetail
import json


@pytest.fixture
def fake_redis():
    class FakeRedis:
        def __init__(self):
            self.data = {}

        async def set(self, key, value, ex=None):
            self.data[key] = value

        async def get(self, key):
            return self.data.get(key)

        async def delete(self, key):
            self.data.pop(key, None)

    return FakeRedis()


@pytest.mark.asyncio
async def test_set_and_get_user_session_data(fake_redis):
    repo = CacheRepository(redis=fake_redis)
    user_detail = UserDetail(id=1, username="john", email="john@example.com", is_admin=True)
    await repo.set_user_session_data("session1", user_detail)
    result = await repo.get_user_session_data("session1")
    assert isinstance(result, UserDetail)
    assert result.username == "john"


@pytest.mark.asyncio
async def test_get_user_session_data_not_found(fake_redis):
    repo = CacheRepository(redis=fake_redis)
    result = await repo.get_user_session_data("unknown")
    assert result is None


@pytest.mark.asyncio
async def test_set_and_get_raw_data(fake_redis):
    repo = CacheRepository(redis=fake_redis)
    await repo.set("mykey", {"a": 1})
    value = await repo.get("mykey")
    assert value == {"a": 1}


@pytest.mark.asyncio
async def test_delete_key(fake_redis):
    repo = CacheRepository(redis=fake_redis)
    await repo.set("key", {"foo": "bar"})
    await repo.delete("key")
    assert await repo.get("key") is None
