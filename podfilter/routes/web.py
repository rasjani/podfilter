"""Web interface routes."""

from __future__ import annotations

from litestar import Request, get
from litestar.di import Provide
from litestar.exceptions import HTTPException
from litestar.response import Redirect, Template
from litestar.status_codes import HTTP_401_UNAUTHORIZED
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession  # noqa: TC002

from podfilter.auth import get_user_by_username, verify_token
from podfilter.database import get_db_session
from podfilter.models import Feed, FilterRule, User


async def get_current_user_optional(request: Request, session: AsyncSession) -> User | None:
  """Get current authenticated user from session cookie, return None if not authenticated."""
  # Check for session cookie or Authorization header
  auth_header = request.headers.get("Authorization")
  token = auth_header.split(" ")[1] if auth_header and auth_header.startswith("Bearer ") else request.cookies.get("access_token")

  if not token:
    return None

  username = verify_token(token)
  if not username:
    return None

  return await get_user_by_username(session, username)


@get("/", dependencies={"session": Provide(get_db_session)})
async def index(
  request: Request,
  session: AsyncSession,
) -> Template:
  """Home page - dashboard for authenticated users, landing page for others."""
  user = await get_current_user_optional(request, session)

  if not user:
    return Template(template_name="index.html")

  # Get user's feeds for dashboard
  feeds_result = await session.execute(select(Feed).where(Feed.user_id == user.id, Feed.is_active.is_(True)))
  feeds = feeds_result.scalars().all()

  return Template(
    template_name="dashboard.html",
    context={
      "user": user,
      "feeds": feeds,
    },
  )


@get("/login")
async def login_page(request: Request) -> Template:
  """Login page."""
  _ = request
  return Template(template_name="login.html")


@get("/register")
async def register_page(request: Request) -> Template:
  """Registration page."""
  _ = request
  return Template(template_name="register.html")


@get("/feeds", dependencies={"session": Provide(get_db_session)})
async def feeds_page(
  request: Request,
  session: AsyncSession,
) -> Template:
  """Feeds management page."""
  user = await get_current_user_optional(request, session)
  if not user:
    raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Authentication required")

  feeds_result = await session.execute(select(Feed).where(Feed.user_id == user.id, Feed.is_active.is_(True)))
  feeds = feeds_result.scalars().all()

  rules_result = await session.execute(select(FilterRule).where(FilterRule.user_id == user.id))
  filter_rules = rules_result.scalars().all()

  return Template(template_name="feeds.html", context={"user": user, "feeds": feeds, "filter_rules": filter_rules})


@get("/filters")
async def filters_page() -> Redirect:
  """Backwards compatible redirect to the combined feeds view."""
  return Redirect(path="/feeds")
