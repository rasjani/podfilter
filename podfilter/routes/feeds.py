"""Feed management routes."""

from typing import Annotated, List, Optional

from litestar import Request, get, post, put, delete
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db_session
from ..models import User, Feed, Episode, FilterRule
from ..utils import FeedParser, OPMLHandler, FilterEngine


class FeedCreate(BaseModel):
    """Feed creation model."""
    url: str


class FeedResponse(BaseModel):
    """Feed response model."""
    id: int
    title: str
    original_url: str
    description: Optional[str]
    is_active: bool


class FilterRuleCreate(BaseModel):
    """Filter rule creation model."""
    feed_id: Optional[int] = None  # None means applies to all feeds
    rule_type: str  # 'title_contains', 'title_regex', 'description_contains'
    pattern: str
    action: str = "exclude"  # 'exclude' or 'include'


class FilterRuleResponse(BaseModel):
    """Filter rule response model."""
    id: int
    feed_id: Optional[int]
    rule_type: str
    pattern: str
    action: str
    is_active: bool


async def get_current_user(request: Request, session: Annotated[AsyncSession, get_db_session]) -> User:
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


@post("/api/feeds")
async def add_feed(
    data: FeedCreate,
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> FeedResponse:
    """Add a new RSS feed."""
    user = await get_current_user(request, session)
    
    try:
        feed_data = await FeedParser.fetch_and_parse_feed(data.url)
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse feed: {str(e)}"
        )
    
    # Create feed
    feed = Feed(
        user_id=user.id,
        title=feed_data['title'],
        original_url=data.url,
        description=feed_data['description']
    )
    session.add(feed)
    await session.flush()
    
    # Add episodes
    for episode_data in feed_data['episodes']:
        episode = Episode(
            feed_id=feed.id,
            title=episode_data['title'],
            description=episode_data['description'],
            guid=episode_data['guid'],
            link=episode_data['link'],
            enclosure_url=episode_data['enclosure_url'],
            enclosure_type=episode_data['enclosure_type'],
            published_at=episode_data['published_at']
        )
        session.add(episode)
    
    await session.commit()
    
    return FeedResponse(
        id=feed.id,
        title=feed.title,
        original_url=feed.original_url,
        description=feed.description,
        is_active=feed.is_active
    )


@post("/api/feeds/import-opml")
async def import_opml(
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> dict[str, str]:
    """Import feeds from OPML file."""
    user = await get_current_user(request, session)
    
    form_data = await request.form()
    opml_file = form_data.get("opml_file")
    
    if not opml_file:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No OPML file provided")
    
    opml_content = await opml_file.read()
    
    try:
        feeds_data = OPMLHandler.parse_opml(opml_content.decode('utf-8'))
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse OPML: {str(e)}"
        )
    
    imported_count = 0
    for feed_data in feeds_data:
        try:
            parsed_feed = await FeedParser.fetch_and_parse_feed(feed_data['url'])
            
            feed = Feed(
                user_id=user.id,
                title=parsed_feed['title'],
                original_url=feed_data['url'],
                description=parsed_feed['description']
            )
            session.add(feed)
            await session.flush()
            
            # Add episodes
            for episode_data in parsed_feed['episodes']:
                episode = Episode(
                    feed_id=feed.id,
                    title=episode_data['title'],
                    description=episode_data['description'],
                    guid=episode_data['guid'],
                    link=episode_data['link'],
                    enclosure_url=episode_data['enclosure_url'],
                    enclosure_type=episode_data['enclosure_type'],
                    published_at=episode_data['published_at']
                )
                session.add(episode)
            
            imported_count += 1
        except Exception:
            # Skip feeds that fail to import
            continue
    
    await session.commit()
    
    return {"message": f"Imported {imported_count} feeds successfully"}


@get("/api/feeds")
async def list_feeds(
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> List[FeedResponse]:
    """List user's feeds."""
    user = await get_current_user(request, session)
    
    result = await session.execute(
        select(Feed).where(Feed.user_id == user.id, Feed.is_active == True)
    )
    feeds = result.scalars().all()
    
    return [
        FeedResponse(
            id=feed.id,
            title=feed.title,
            original_url=feed.original_url,
            description=feed.description,
            is_active=feed.is_active
        )
        for feed in feeds
    ]


@post("/api/filter-rules")
async def add_filter_rule(
    data: FilterRuleCreate,
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> FilterRuleResponse:
    """Add a new filter rule."""
    user = await get_current_user(request, session)
    
    # Validate feed_id if provided
    if data.feed_id:
        result = await session.execute(
            select(Feed).where(Feed.id == data.feed_id, Feed.user_id == user.id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Feed not found")
    
    filter_rule = FilterRule(
        user_id=user.id,
        feed_id=data.feed_id,
        rule_type=data.rule_type,
        pattern=data.pattern,
        action=data.action
    )
    session.add(filter_rule)
    await session.commit()
    
    return FilterRuleResponse(
        id=filter_rule.id,
        feed_id=filter_rule.feed_id,
        rule_type=filter_rule.rule_type,
        pattern=filter_rule.pattern,
        action=filter_rule.action,
        is_active=filter_rule.is_active
    )


@get("/api/filter-rules")
async def list_filter_rules(
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> List[FilterRuleResponse]:
    """List user's filter rules."""
    user = await get_current_user(request, session)
    
    result = await session.execute(
        select(FilterRule).where(FilterRule.user_id == user.id)
    )
    rules = result.scalars().all()
    
    return [
        FilterRuleResponse(
            id=rule.id,
            feed_id=rule.feed_id,
            rule_type=rule.rule_type,
            pattern=rule.pattern,
            action=rule.action,
            is_active=rule.is_active
        )
        for rule in rules
    ]


@delete("/api/filter-rules/{rule_id:int}", status_code=HTTP_204_NO_CONTENT)
async def delete_filter_rule(
    rule_id: int,
    request: Request,
    session: Annotated[AsyncSession, get_db_session],
) -> None:
    """Delete a filter rule."""
    user = await get_current_user(request, session)
    
    result = await session.execute(
        select(FilterRule).where(FilterRule.id == rule_id, FilterRule.user_id == user.id)
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Filter rule not found")
    
    await session.delete(rule)
    await session.commit()