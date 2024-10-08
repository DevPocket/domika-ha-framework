# vim: set fileencoding=utf-8
"""
Test cache.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest

from domika_ha_framework.cache import CacheKey, cache_key, cached

pytestmark = pytest.mark.usefixtures("_clear_cache")


def _counter_stub():
    pass


@pytest.fixture
def _clear_cache() -> None:
    """Clear all caches for test isolation."""
    _fn1.cache_clear()
    _fn2.cache_clear()


@pytest.fixture
def mock_counter_stub() -> Generator[Mock, None, None]:
    """Mock the dashboard.router.dashboard_service."""
    with patch(__name__ + "._counter_stub", autospec=True) as mock_counter_stub_:
        yield mock_counter_stub_


@cached
async def _fn1(i: int) -> int:
    _counter_stub()
    return i + 10


def _fn2_cache_keys(*args, **kwargs) -> CacheKey:
    """
    Generate cache key, ignoring first arg.

    Returns:
        generated cache key.
    """
    args = args[1:]
    return cache_key(*args, **kwargs)


@cached(_fn2_cache_keys)
async def _fn2(i: int, z: int) -> int:
    # Argument i will be excluded from cache key calculation, so _fn2(1, 5) must be equal to
    # _fn2(5, 5).
    _counter_stub()
    return i * z


@pytest.mark.asyncio(loop_scope="session")
async def test_cached(mock_counter_stub: Mock) -> None:
    res = await _fn1(3)

    for _ in range(1000):
        res1 = await _fn1(3)
        assert res == res1

    # Check that actual function called only once.
    mock_counter_stub.assert_called_once()

    _fn1.cache_clear()
    await _fn1(3)

    # Check that called once more after cache_clear called.
    assert mock_counter_stub.call_count == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_cached_with_args(mock_counter_stub: Mock) -> None:
    res = await _fn2(3, 2)
    assert res == await _fn2(5, 2)
    assert res != await _fn2(7, 3)
    assert res == await _fn2(15, 2)

    # Check that called twice.
    assert mock_counter_stub.call_count == 2


@pytest.mark.asyncio(loop_scope="session")
async def test_cache_clear() -> None:
    await _fn1(3)
    _fn1.cache_clear()
    assert _fn1.cache_size() == 0


@pytest.mark.asyncio(loop_scope="session")
async def test_without_cache(mock_counter_stub: Mock) -> None:
    await _fn1(3)
    await _fn1.without_cache(3)
    assert mock_counter_stub.call_count == 2
