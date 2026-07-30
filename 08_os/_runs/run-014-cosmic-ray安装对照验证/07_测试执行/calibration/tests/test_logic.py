from calibration_pkg import (
    Role,
    access_level,
    clamp_nonnegative,
    decorated_double,
    identity_offset,
)


def test_clamp_typical_values() -> None:
    assert clamp_nonnegative(-7) == 0
    assert clamp_nonnegative(4) == 4


def test_guest_access_level() -> None:
    assert access_level(Role.GUEST) == 0


def test_decorated_double_wrapped_body() -> None:
    assert decorated_double(3) == 6


def test_identity_offset() -> None:
    assert identity_offset(9) == 9
