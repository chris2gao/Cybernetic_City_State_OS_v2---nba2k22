from __future__ import annotations

from enum import Enum
from functools import wraps
from typing import Callable


class Role(Enum):
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"


def clamp_nonnegative(value: int) -> int:
    if value < 0:
        return 0
    return value


def access_level(role: Role) -> int:
    if role is Role.ADMIN:
        return 2
    if role is Role.MEMBER:
        return 1
    return 0


def require_nonnegative(function: Callable[[int], int]) -> Callable[[int], int]:
    @wraps(function)
    def wrapped(value: int) -> int:
        if value < 0:
            raise ValueError("value must be nonnegative")
        return function(value)

    return wrapped


@require_nonnegative
def decorated_double(value: int) -> int:
    return value * 2


def identity_offset(value: int) -> int:
    return value + 0
