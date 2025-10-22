"""Authentication routes."""

from typing import Annotated

from litestar import Request, Response, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import authenticate_user, create_access_token, hash_password
from litestar.di import Provide

from ..database import get_db_session
from ..models import User


class UserCreate(BaseModel):
  """User creation model."""

  username: str
  email: str
  password: str


class UserLogin(BaseModel):
  """User login model."""

  username: str
  password: str


class Token(BaseModel):
  """Token response model."""

  access_token: str
  token_type: str


@post("/api/register", dependencies={"session": Provide(get_db_session)})
async def register(
  data: UserCreate,
  session: AsyncSession,
) -> dict[str, str]:
  """Register a new user."""
  # Check if user already exists
  result = await session.execute(select(User).where(User.username == data.username))
  if result.scalar_one_or_none():
    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Username already exists")

  result = await session.execute(select(User).where(User.email == data.email))
  if result.scalar_one_or_none():
    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Email already exists")

  # Create new user
  hashed_password = hash_password(data.password)
  user = User(username=data.username, email=data.email, password_hash=hashed_password)
  session.add(user)
  await session.commit()

  return {"message": "User created successfully"}


@post("/api/login", dependencies={"session": Provide(get_db_session)})
async def login(
  data: UserLogin,
  session: AsyncSession,
) -> Token:
  """Login user and return JWT token."""
  user = await authenticate_user(session, data.username, data.password)
  if not user:
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

  access_token = create_access_token(data={"sub": user.username})
  return Token(access_token=access_token, token_type="bearer")


@post("/api/logout")
async def logout(request: Request) -> dict[str, str]:
  """Logout user (client-side token removal)."""
  return {"message": "Logged out successfully"}
