"""Authentication schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Credentials submitted to the login endpoint."""

    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=8, max_length=256)


class TokenResponse(BaseModel):
    """Bearer token returned after successful authentication."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """Public authenticated-user representation."""

    id: uuid.UUID
    username: str
    role: str
    is_active: bool
    created_at: datetime
