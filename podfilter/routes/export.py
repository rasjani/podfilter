"""Export routes for RSS and OPML."""

from typing import Annotated

from litestar import Request, Response, get
from litestar.exceptions import HTTPException
from litestar.response import File
from litestar.status_codes import HTTP_404_NOT_FOUND
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from litestar.di import Provide

from ..database import get_db_session
from ..models import User, Feed, Episode, FilterRule
from ..utils import RSSGenerator, OPMLHandler, FilterEngine


async def get_current_user(request: Request, session: AsyncSession) -> User:
    """Get current authenticated user from request."""
    from ..auth import verify_token, get_user_by_username
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = auth_header.split(" ")[1]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await get_user_by_username(session, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@get("/export/rss/{feed_id:int}", dependencies={"session": Provide(get_db_session)})
async def export_rss_feed(
    feed_id: int,
    request: Request,
    session: AsyncSession,
) -> Response:
    """Export filtered RSS feed."""
    user = await get_current_user(request, session)
    
    # Get feed
    result = await session.execute(
        select(Feed).where(Feed.id == feed_id, Feed.user_id == user.id)
    )
    feed = result.scalar_one_or_none()
    if not feed:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Feed not found")
    
    # Get episodes
    result = await session.execute(
        select(Episode).where(Episode.feed_id == feed_id)
    )
    episodes = result.scalars().all()
    
    # Get filter rules
    result = await session.execute(
        select(FilterRule).where(
            (FilterRule.user_id == user.id) & 
            ((FilterRule.feed_id == feed_id) | (FilterRule.feed_id.is_(None))) &
            (FilterRule.is_active == True)
        )
    )
    filter_rules = result.scalars().all()
    
    # Convert to dicts for filtering
    episodes_data = [
        {
            'title': episode.title,
            'description': episode.description,
            'guid': episode.guid,
            'link': episode.link,
            'enclosure_url': episode.enclosure_url,
            'enclosure_type': episode.enclosure_type,
            'published_at': episode.published_at,
        }
        for episode in episodes
    ]
    
    filter_rules_data = [
        {
            'rule_type': rule.rule_type,
            'pattern': rule.pattern,
            'action': rule.action,
            'is_active': rule.is_active,
        }
        for rule in filter_rules
    ]
    
    # Apply filters
    filtered_episodes = FilterEngine.apply_filters(episodes_data, filter_rules_data)
    
    # Generate RSS
    feed_info = {
        'title': feed.title,
        'description': feed.description or '',
        'link': feed.original_url,
    }
    
    rss_content = RSSGenerator.generate_rss(feed_info, filtered_episodes)
    
    return Response(
        content=rss_content,
        media_type="application/rss+xml",
        headers={"Content-Disposition": f"attachment; filename=\"{feed.title}.xml\""}
    )


@get("/export/opml", dependencies={"session": Provide(get_db_session)})
async def export_opml(
    request: Request,
    session: AsyncSession,
) -> Response:
    """Export all feeds as OPML."""
    user = await get_current_user(request, session)
    
    # Get all user feeds
    result = await session.execute(
        select(Feed).where(Feed.user_id == user.id, Feed.is_active == True)
    )
    feeds = result.scalars().all()
    
    # Convert to OPML format
    feeds_data = [
        {
            'title': feed.title,
            'url': f"/export/rss/{feed.id}",  # Link to filtered RSS
            'description': feed.description or '',
        }
        for feed in feeds
    ]
    
    opml_content = OPMLHandler.generate_opml(feeds_data, f"{user.username}'s PodFilter Feeds")
    
    return Response(
        content=opml_content,
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=\"{user.username}_feeds.opml\""}
    )