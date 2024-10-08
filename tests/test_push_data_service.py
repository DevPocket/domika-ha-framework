# vim: set fileencoding=utf-8
"""
Test push data.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

import asyncio
import contextlib
import uuid
from typing import AsyncContextManager, Awaitable

import pytest
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import AsyncSession

import domika_ha_framework.push_data.flow as push_data_flow
import domika_ha_framework.push_data.service as push_data_service
import domika_ha_framework.subscription.flow as subscription_flow
from domika_ha_framework import push_data
from domika_ha_framework.push_data.models import DomikaPushDataCreate


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.push_data_interval(2)
@pytest.mark.push_data_threshold(0)
async def test_create_event(
    db_session: AsyncSession,
    http_session: ClientSession,
    push_data_processor: AsyncContextManager[None],
    timestamp_now: int,
):
    # Create subscription.
    await subscription_flow.resubscribe(
        db_session,
        app_session_id=uuid.uuid4(),
        subscriptions={
            "ent1": {
                "attr1": 1,
                "attr2": 1,
            },
        },
    )

    # Create events.
    push_data_ = [
        DomikaPushDataCreate(
            event_id=uuid.uuid4(),
            entity_id="ent1",
            attribute="attr1",
            value="on",
            context_id="123",
            timestamp=timestamp_now,
            delay=0,
        ),
        DomikaPushDataCreate(
            event_id=uuid.uuid4(),
            entity_id="ent1",
            attribute="attr2",
            value="on",
            context_id="123",
            timestamp=timestamp_now,
            delay=0,
        ),
    ]

    # Register event.
    await push_data_flow.register_event(
        http_session,
        push_data=push_data_,
        critical_push_needed=False,
        critical_alert_payload={},
    )

    # Start push_data_processor.
    async with push_data_processor:
        await asyncio.sleep(0)  # Run one event loop cycle.

        # Test that queue is empty.
        events: list[DomikaPushDataCreate] = []
        with contextlib.suppress(asyncio.QueueEmpty):
            while True:
                events.append(push_data.events_queue.get_nowait())

        assert len(events) == 0

    stored_push_data = await push_data_service.get_all(db_session)
    assert len(stored_push_data) == len(push_data_)

    stored_push_data_ids = [pd.event_id for pd in stored_push_data]

    assert all(pd.event_id in stored_push_data_ids for pd in push_data_)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.push_data_interval(2)
@pytest.mark.push_data_threshold(0)
async def test_create_a_lot_of_events(
    db_session: AsyncSession,
    http_session: ClientSession,
    push_data_processor: AsyncContextManager[None],
    timestamp_now: int,
):
    attrs = {f"attr_{n}": 1 for n in range(100)}
    entities = {f"ent_{n}": attrs for n in range(10)}

    # Create subscription.
    await subscription_flow.resubscribe(
        db_session,
        app_session_id=uuid.uuid4(),
        subscriptions=entities,
    )

    aws: list[Awaitable] = []
    for ent_id in range(10):
        for attr_id in range(100):
            # Create events.
            aws.append(
                push_data_flow.register_event(
                    http_session,
                    push_data=[
                        DomikaPushDataCreate(
                            event_id=uuid.uuid4(),
                            entity_id=f"ent_{ent_id}",
                            attribute=f"attr_{attr_id}",
                            value="on",
                            context_id="123",
                            timestamp=timestamp_now,
                            delay=0,
                        ),
                    ],
                    critical_push_needed=False,
                    critical_alert_payload={},
                ),
            )

    # Register events simultaneously.
    await asyncio.gather(*aws)

    # Start push_data_processor.
    async with push_data_processor:
        await asyncio.sleep(0)  # Run one event loop cycle.

        # Test that queue is empty.
        events: list[DomikaPushDataCreate] = []
        with contextlib.suppress(asyncio.QueueEmpty):
            while True:
                events.append(push_data.events_queue.get_nowait())

        assert len(events) == 0

    stored_push_data = await push_data_service.get_all(db_session, limit=-1)

    assert len(stored_push_data) == 1000
