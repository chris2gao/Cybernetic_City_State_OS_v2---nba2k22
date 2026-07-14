"""Math Mentor P0 control-plane primitives.

This package is deliberately stateless.  It does not activate the teaching
runtime, mutate student state, or authorize repository writes.
"""

from .normalization import (
    NORMALIZED_SCHEMA_VERSION,
    detect_schema_era,
    normalize_node,
    parse_and_normalize_node,
)

__all__ = [
    "NORMALIZED_SCHEMA_VERSION",
    "detect_schema_era",
    "normalize_node",
    "parse_and_normalize_node",
]
