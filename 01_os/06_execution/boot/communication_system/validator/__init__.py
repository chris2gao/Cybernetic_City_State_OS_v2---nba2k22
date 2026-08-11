"""Deterministic validation only; importing this package grants no authority."""

from .validate_communication_system import CommunicationValidationError, CommunicationValidator

__all__ = ["CommunicationValidationError", "CommunicationValidator"]

