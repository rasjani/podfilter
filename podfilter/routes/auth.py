"""Authentication routes."""

from __future__ import annotations

from litestar import Request, Response, post
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from podfilter.auth import ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token, hash_password
from podfilter.database import get_db_session
from podfilter.models import User


def _default_token_type() -> str:
  return "bearer"


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
  token_type: str = Field(default_factory=_default_token_type)


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
) -> Response[dict[str, str]]:
  """Login user and return JWT token."""
  user = await authenticate_user(session, data.username, data.password)
  if not user:
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

  access_token = create_access_token(data={"sub": user.username})

  response = Response(
    content=Token(access_token=access_token).model_dump(),
    media_type="application/json",
  )
  response.delete_cookie("access_token", path="/")
  response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=False,
    samesite="lax",
    max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    path="/",
  )
  return response


@post("/api/logout")
async def logout(request: Request) -> Response[dict[str, str]]:
  """Logout user (client-side token removal)."""
  _ = request
  response = Response({"message": "Logged out successfully"}, media_type="application/json")
  response.delete_cookie("access_token", path="/")
  return response
