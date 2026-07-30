from calibration_pkg import access_level, clamp_nonnegative


def test_clamp_nonnegative() -> None:
    assert clamp_nonnegative(-7) == 0
    assert clamp_nonnegative(4) == 4


def test_guest_access_level() -> None:
    assert access_level("guest") == 1
