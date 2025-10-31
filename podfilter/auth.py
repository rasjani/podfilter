"""Authentication utilities."""

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

try:
  from datetime import UTC
except ImportError:  # pragma: no cover - Python < 3.11 fallback
  from datetime import timezone

  UTC = timezone.utc  # noqa: UP017

import bcrypt
from jose import JWTError, jwt
from sqlalchemy import select

if TYPE_CHECKING:
  from sqlalchemy.ext.asyncio import AsyncSession

from podfilter.models import User

# JWT Configuration
SECRET_KEY = os.getenv("PODFILTER_SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
  """Hash a password using bcrypt."""
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
  """Verify a password against its hash."""
  return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
  """Create a JWT access token."""
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(UTC) + expires_delta
  else:
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> str | None:
  """Verify a JWT token and return the username."""
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
  except JWTError:
    return None
  username = payload.get("sub")
  if not isinstance(username, str):
    return None
  return username


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User | None:
  """Authenticate a user with username and password."""
  result = await session.execute(select(User).where(User.username == username))
  user = result.scalar_one_or_none()
  if user and verify_password(password, user.password_hash):
    return user
  return None


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
  """Get a user by username."""
  result = await session.execute(select(User).where(User.username == username))
  return result.scalar_one_or_none()
