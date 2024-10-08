# vim: set fileencoding=utf-8
"""
Test utils.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

import pytest

from domika_ha_framework.utils import chunks


@pytest.mark.parametrize(
    ("test_input", "chunk_size", "expected"),
    [
        (
            [1, 2, 3, 4, 5, 6],
            2,
            [
                [1, 2],
                [3, 4],
                [5, 6],
            ],
        ),
        (
            [1, 2, 3, 4, 5, 6, 7],
            2,
            [
                [1, 2],
                [3, 4],
                [5, 6],
                [7],
            ],
        ),
        (
            [1, 2, 3],
            1,
            [
                [1],
                [2],
                [3],
            ],
        ),
        (
            list(range(1000)),
            500,
            [
                list(range(500)),
                list(range(500, 1000)),
            ],
        ),
    ],
)
def test_chunks(test_input: list[int], chunk_size: int, expected: list[list[int]]):
    res: list[list[int]] = []
    for chunk in chunks(test_input, chunk_size):
        res.append(list(chunk))
    assert res == expected
