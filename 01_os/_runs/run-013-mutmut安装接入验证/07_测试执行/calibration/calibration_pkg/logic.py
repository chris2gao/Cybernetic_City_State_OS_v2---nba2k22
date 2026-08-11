def clamp_nonnegative(value: int) -> int:
    if value < 0:
        return 0
    return value


def access_level(role: str) -> int:
    if role == "admin":
        return 2
    return 1
