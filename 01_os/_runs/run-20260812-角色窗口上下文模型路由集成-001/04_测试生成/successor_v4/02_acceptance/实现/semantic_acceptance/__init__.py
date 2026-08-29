"""Representation-neutral semantic acceptance prototype.

Root-cause replacement for the Stage04 acceptance methodology of
os-v2-role-window-context-model-routing-integration-001.

This is root-cause evidence.  It is NOT a Stage04 v4 frozen package, it does not
declare Stage04 PASS, and it authorizes nothing.
"""

from .core import Document, discover_documents, load_yaml_strict  # noqa: F401
from .facts import FactSet, build_fact_set  # noqa: F401
from .predicates import FAIL, PASS, UNSUPPORTED, PredicateResult, evaluate_all  # noqa: F401

__all__ = [
    "Document",
    "FactSet",
    "PASS",
    "FAIL",
    "UNSUPPORTED",
    "PredicateResult",
    "build_fact_set",
    "discover_documents",
    "evaluate_all",
    "load_yaml_strict",
]
