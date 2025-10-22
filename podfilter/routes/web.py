"""Web interface routes."""

from typing import Annotated, Optional

from litestar import Request, get, post
from litestar.response import Template
from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..models import User, Feed, FilterRule
from ..auth import verify_token, get_user_by_username


async def get_current_user_optional(request: Request, session: AsyncSession) -> Optional[User]:
    """Get current authenticated user from session cookie, return None if not authenticated."""
    # Check for session cookie or Authorization header
    auth_header = request.headers.get("Authorization")
    token = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        # Check for session cookie
        token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    username = verify_token(token)
    if not username:
        return None
    
    user = await get_user_by_username(session, username)
    return user


@get("/")
async def index(
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> Template:
    """Home page - dashboard for authenticated users, landing page for others."""
    user = await get_current_user_optional(request, session)
    
    if user:
        # Get user's feeds and filter rules for dashboard
        feeds_result = await session.execute(
            select(Feed).where(Feed.user_id == user.id, Feed.is_active == True)
        )
        feeds = feeds_result.scalars().all()
        
        rules_result = await session.execute(
            select(FilterRule).where(FilterRule.user_id == user.id)
        )
        filter_rules = rules_result.scalars().all()
        
        return Template(
            template_name="dashboard.html",
            context={
                "user": user,
                "feeds": feeds,
                "filter_rules": filter_rules,
            }
        )
    else:
        return Template(template_name="index.html")


@get("/login")
async def login_page(request: Request) -> Template:
    """Login page."""
    return Template(template_name="login.html")


@get("/register")
async def register_page(request: Request) -> Template:
    """Registration page."""
    return Template(template_name="register.html")


@get("/feeds")
async def feeds_page(
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> Template:
    """Feeds management page."""
    user = await get_current_user_optional(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    feeds_result = await session.execute(
        select(Feed).where(Feed.user_id == user.id, Feed.is_active == True)
    )
    feeds = feeds_result.scalars().all()
    
    return Template(
        template_name="feeds.html",
        context={"user": user, "feeds": feeds}
    )


@get("/filters")
async def filters_page(
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> Template:
    """Filter rules management page."""
    user = await get_current_user_optional(request, session)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    feeds_result = await session.execute(
        select(Feed).where(Feed.user_id == user.id, Feed.is_active == True)
    )
    feeds = feeds_result.scalars().all()
    
    rules_result = await session.execute(
        select(FilterRule).where(FilterRule.user_id == user.id)
    )
    filter_rules = rules_result.scalars().all()
    
    return Template(
        template_name="filters.html",
        context={
            "user": user,
            "feeds": feeds,
            "filter_rules": filter_rules,
        }
    )