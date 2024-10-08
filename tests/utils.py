# vim: set fileencoding=utf-8
"""
Test utils.

(c) DevPocket, 2024


Author(s): Artem Bezborodko
"""

from enum import Enum


class NotSet(Enum):
    """Not set sentinel enum."""

    token = 0


# Not set sentinel value.
NOT_SET = NotSet.token
