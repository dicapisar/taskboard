import pytest
from src.app.services.cache_service import CacheService
from src.app.dtos.user_detail import UserDetail


@pytest.fixture
def mock_repo():
    class MockRepo:
        def __init__(self):
            self.storage = {}

        async def set_user_session_data(self, session_id, data):
            self.storage[session_id] = data

        async def get_user_session_data(self, session_id):
            return self.storage.get(session_id)

        async def set(self, key, value, ttl_seconds=60):
            self.storage[key] = value

        async def get(self, key):
            return self.storage.get(key)

        async def delete(self, key):
            self.storage.pop(key, None)

    return MockRepo()


@pytest.mark.asyncio
async def test_set_and_get_user_session_data(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    session_id = "session123"
    user_data = UserDetail(id=1, username="john", email="john@example.com", is_admin=True)

    await service.set_user_session_data(session_id, user_data)
    result = await service.get_user_session_data(session_id)

    assert isinstance(result, UserDetail)
    assert result.username == "john"


@pytest.mark.asyncio
async def test_get_user_session_data_invalid_session(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    result = await service.get_user_session_data("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_set_and_get_raw_key(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    await service.set("mykey", {"x": 1})
    value = await service.get("mykey")
    assert value == {"x": 1}


@pytest.mark.asyncio
async def test_delete_key(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    await service.set("todelete", {"foo": "bar"})
    await service.delete("todelete")
    assert await service.get("todelete") is None


@pytest.mark.asyncio
async def test_set_user_session_data_invalid(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    with pytest.raises(ValueError):
        await service.set_user_session_data("", UserDetail(id=1, username="x", email="x@y.com"))

    with pytest.raises(ValueError):
        await service.set_user_session_data("id", None)


@pytest.mark.asyncio
async def test_get_user_session_data_invalid(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    with pytest.raises(ValueError):
        await service.get_user_session_data("")


@pytest.mark.asyncio
async def test_set_invalid(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    with pytest.raises(ValueError):
        await service.set("", {"x": 1})
    with pytest.raises(ValueError):
        await service.set("key", None)


@pytest.mark.asyncio
async def test_get_invalid(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    with pytest.raises(ValueError):
        await service.get("")


@pytest.mark.asyncio
async def test_delete_invalid(mock_repo):
    service = CacheService(cache_repository=mock_repo)
    with pytest.raises(ValueError):
        await service.delete("")
