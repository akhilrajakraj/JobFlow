"""Configuration validation tests."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_secrets() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production")


def test_development_allows_defaults() -> None:
    assert Settings(environment="development").environment == "development"
