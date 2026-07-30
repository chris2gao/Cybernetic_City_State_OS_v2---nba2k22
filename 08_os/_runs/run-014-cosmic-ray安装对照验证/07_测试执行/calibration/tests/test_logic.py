import pytest

from calibration_pkg import (
    Role,
    access_level,
    clamp_nonnegative,
    decorated_double,
    identity_offset,
)


def test_clamp_typical_values() -> None:
    assert clamp_nonnegative(-7) == 0
    assert clamp_nonnegative(0) == 0
    assert clamp_nonnegative(4) == 4


def test_each_role_access_level() -> None:
    assert access_level(Role.ADMIN) == 2
    assert access_level(Role.MEMBER) == 1
    assert access_level(Role.GUEST) == 0


def test_decorated_double_wrapper_and_body() -> None:
    assert decorated_double.__name__ == "decorated_double"
    with pytest.raises(ValueError, match="must be nonnegative"):
        decorated_double(-1)
    assert decorated_double(3) == 6


def test_identity_offset() -> None:
    assert identity_offset(9) == 9
