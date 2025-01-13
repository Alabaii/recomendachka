import asyncio
import pytest
import pytest_asyncio
from app.database import Base, async_session_maker, engine
from app.config import settings

from app.users.models import Users
from app.city.models import City
from app.recommendation.models import Recommendation 



@pytest_asyncio.fixture(scope= "session",autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


# @pytest.fixture(scope="session")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()