# vim: set fileencoding=utf-8
"""
Conftest.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

import asyncio
import datetime
import os
from contextlib import asynccontextmanager
from typing import AsyncContextManager, TypeVar

import aiohttp
import pytest
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

import domika_ha_framework.device.service as device_service
from domika_ha_framework import config, push_data
from domika_ha_framework.database import core as database_core
from domika_ha_framework.database import manage as database_manage
from domika_ha_framework.models import AsyncBase

load_dotenv(override=True)

T = TypeVar("T")


@pytest.fixture(scope="session")
async def db_instance():
    db_path = os.getenv("DOMIKA_DB_PATH", "./test.db3")
    config.CONFIG.database_url = f"sqlite+aiosqlite:///{db_path}"
    await database_core.init_db()
    await database_manage.migrate()
    yield None
    await database_core.close_db()
    os.remove(db_path)


@pytest.fixture(scope="session")
async def session(db_instance: None):  # noqa: ARG001
    async with database_core.AsyncSessionFactory() as session:
        yield session


@pytest.fixture
async def db_session(session: AsyncSession):
    async with session as db_session:
        # Clear caches.
        device_service.get_all_with_push_session_id.cache_clear()

        # Clear DB before test function.
        for table in reversed(AsyncBase.metadata.sorted_tables):
            await db_session.execute(table.delete())
        await db_session.commit()

        yield db_session

        # Clear DB after test function.
        for table in reversed(AsyncBase.metadata.sorted_tables):
            await db_session.execute(table.delete())
        await db_session.commit()


@pytest.fixture(scope="session")
async def http_session():
    async with aiohttp.ClientSession() as http_session:
        yield http_session


def _get_marker_value(request: pytest.FixtureRequest, maker_name: str, default: T) -> T:
    marker = request.node.get_closest_marker(maker_name)
    if marker:
        return marker.args[0]
    return default


@asynccontextmanager
async def _push_data_processor(interval: float, threshold: int, store_chunk_size: int):
    push_data.start_push_data_processor(interval, threshold, store_chunk_size)
    # Run one event loop cycle, so push_data_processor started.
    await asyncio.sleep(0)
    try:
        yield None
    finally:
        await push_data.stop_push_data_processor()


@pytest.fixture
async def push_data_processor(request: pytest.FixtureRequest) -> AsyncContextManager[None]:
    return _push_data_processor(
        _get_marker_value(request, "push_data_interval", push_data.INTERVAL),
        _get_marker_value(request, "push_data_threshold", push_data.THRESHOLD),
        _get_marker_value(request, "push_data_store_chunk_size", push_data.STORE_CHUNK_SIZE),
    )


@pytest.fixture
def timestamp_now() -> int:
    return int(datetime.datetime.now(datetime.UTC).timestamp() * 1e6)
