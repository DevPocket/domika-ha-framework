# vim: set fileencoding=utf-8
"""
Test device service.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

import uuid
from typing import Awaitable, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import domika_ha_framework.device.service as device_service
from domika_ha_framework.device.models import Device, DomikaDeviceCreate, DomikaDeviceUpdate

from .utils import NOT_SET, NotSet


@pytest.fixture
def domika_device_factory(
    db_session: AsyncSession,
    timestamp_now: int,
) -> Callable[..., Awaitable[Device]]:
    async def fn(
        app_session_id: uuid.UUID | NotSet = NOT_SET,
        user_id: str | NotSet = NOT_SET,
        push_session_id: uuid.UUID | None | NotSet = NOT_SET,
        push_token_hash: str | NotSet = NOT_SET,
    ) -> Device:
        device = Device(
            app_session_id=uuid.uuid4() if app_session_id is NOT_SET else app_session_id,
            user_id="user_id" if user_id is NOT_SET else user_id,
            push_session_id=uuid.uuid4() if push_session_id is NOT_SET else push_session_id,
            push_token_hash="push_token_hash" if push_token_hash is NOT_SET else push_token_hash,
            last_update=timestamp_now,
        )
        db_session.add(device)
        await db_session.commit()
        return device

    return fn


@pytest.mark.asyncio(loop_scope="session")
async def test_get(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory()

    device = await device_service.get(db_session, device.app_session_id)

    assert device


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(app_session_id=uuid.UUID(int=1))
    device2 = await domika_device_factory(app_session_id=uuid.UUID(int=2))

    devices = await device_service.get_all(db_session)

    assert len(devices) == 2
    assert devices[0].app_session_id == device1.app_session_id
    assert devices[1].app_session_id == device2.app_session_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory()
    await domika_device_factory(push_session_id=None)

    devices = await device_service.get_all_with_push_session_id(db_session)

    assert len(devices) == 1
    assert devices[0].app_session_id == device1.app_session_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_no_db_session(
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(app_session_id=uuid.UUID(int=1))
    await domika_device_factory(app_session_id=uuid.UUID(int=2), push_session_id=None)

    devices = await device_service.get_all_with_push_session_id()

    assert len(devices) == 1
    assert devices[0].app_session_id == device1.app_session_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_cache_after_remove_all_with_push_token_hash(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(app_session_id=uuid.UUID(int=1))

    await device_service.get_all_with_push_session_id(db_session)

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    await device_service.remove_all_with_push_token_hash(
        db_session,
        "any_hash",
        except_device=device1,
    )

    assert device_service.get_all_with_push_session_id.cache_size() == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_cache_after_create(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    await domika_device_factory(app_session_id=uuid.UUID(int=1))

    await device_service.get_all_with_push_session_id(db_session)

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    await device_service.create(
        db_session,
        DomikaDeviceCreate(
            app_session_id=uuid.UUID(int=2),
            user_id="user_id",
            push_session_id=uuid.uuid4(),
            push_token_hash="push_token_hash",  # noqa: S106
        ),
    )

    assert device_service.get_all_with_push_session_id.cache_size() == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_cache_after_update(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory(app_session_id=uuid.UUID(int=1))

    await device_service.get_all_with_push_session_id(db_session)

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    # When update arguments other than push_session_id than cache should not be cleared.
    await device_service.update(db_session, device, DomikaDeviceUpdate(last_update=0))

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    # Cache must be cleared here.
    await device_service.update(db_session, device, DomikaDeviceUpdate(push_session_id=None))

    assert device_service.get_all_with_push_session_id.cache_size() == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_cache_after_update_in_place(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory(app_session_id=uuid.UUID(int=1))

    await device_service.get_all_with_push_session_id(db_session)

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    # When update arguments other than push_session_id than cache should not be cleared.
    await device_service.update_in_place(
        db_session,
        device.app_session_id,
        DomikaDeviceUpdate(last_update=0),
    )

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    # Cache must be cleared here.
    await device_service.update_in_place(
        db_session,
        device.app_session_id,
        DomikaDeviceUpdate(push_session_id=None),
    )

    assert device_service.get_all_with_push_session_id.cache_size() == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_cache_after_delete(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory(app_session_id=uuid.UUID(int=1))

    await device_service.get_all_with_push_session_id(db_session)

    assert device_service.get_all_with_push_session_id.cache_size() == 1

    await device_service.delete(db_session, device.app_session_id)

    assert device_service.get_all_with_push_session_id.cache_size() == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_session_id_cached(
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(app_session_id=uuid.UUID(int=1))
    await domika_device_factory(app_session_id=uuid.UUID(int=2), push_session_id=None)

    devices = await device_service.get_all_with_push_session_id()

    assert len(devices) == 1
    assert devices[0].app_session_id == device1.app_session_id
    assert device_service.get_all_with_push_session_id.cache_size() == 1

    devices1 = await device_service.get_all_with_push_session_id()

    assert devices == devices1


@pytest.mark.asyncio(loop_scope="session")
async def test_get_by_user_id(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(user_id="test1")
    await domika_device_factory(user_id="test2")

    devices = await device_service.get_by_user_id(db_session, "test1")

    assert len(devices) == 1
    assert device1.user_id == devices[0].user_id


@pytest.mark.asyncio(loop_scope="session")
async def test_get_all_with_push_token_hash(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(push_token_hash="test1")  # noqa: S106
    await domika_device_factory(push_token_hash="test2")  # noqa: S106

    devices = await device_service.get_all_with_push_token_hash(db_session, "test1")

    assert len(devices) == 1
    assert device1.push_token_hash == devices[0].push_token_hash


@pytest.mark.asyncio(loop_scope="session")
async def test_remove_all_with_push_token_hash(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device1 = await domika_device_factory(
        app_session_id=uuid.UUID(int=1),
        push_token_hash="test1",  # noqa: S106
    )
    await domika_device_factory(
        app_session_id=uuid.UUID(int=2),
        push_token_hash="test1",  # noqa: S106
    )
    device2 = await domika_device_factory(
        app_session_id=uuid.UUID(int=3),
        push_token_hash="test2",  # noqa: S106
    )
    await device_service.remove_all_with_push_token_hash(
        db_session,
        "test1",
        except_device=device1,
    )

    devices = await device_service.get_all(db_session)

    assert len(devices) == 2
    assert devices[0].app_session_id == device1.app_session_id
    assert devices[1].app_session_id == device2.app_session_id


@pytest.mark.asyncio(loop_scope="session")
async def test_create(
    db_session: AsyncSession,
) -> None:
    device = await device_service.create(
        db_session,
        DomikaDeviceCreate(
            app_session_id=uuid.UUID(int=1),
            user_id="user_id",
            push_session_id=uuid.uuid4(),
            push_token_hash="push_token_hash",  # noqa: S106
        ),
    )

    devices = await device_service.get_all(db_session)

    assert len(devices) == 1
    assert devices[0].app_session_id == device.app_session_id


@pytest.mark.asyncio(loop_scope="session")
async def test_update(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory()
    await device_service.update(db_session, device, DomikaDeviceUpdate(last_update=0))

    devices = await device_service.get_all(db_session)

    assert len(devices) == 1
    assert devices[0].app_session_id == device.app_session_id
    assert devices[0].last_update == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_update_in_place(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory()
    await device_service.update_in_place(
        db_session,
        device.app_session_id,
        DomikaDeviceUpdate(last_update=0),
    )

    devices = await device_service.get_all(db_session)

    assert len(devices) == 1
    assert devices[0].app_session_id == device.app_session_id
    assert devices[0].last_update == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_delete(
    db_session: AsyncSession,
    domika_device_factory: Callable[..., Awaitable[Device]],
) -> None:
    device = await domika_device_factory()
    await device_service.delete(db_session, device.app_session_id)

    devices = await device_service.get_all(db_session)

    assert not devices
