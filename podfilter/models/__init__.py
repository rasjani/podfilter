"""Database models for the PodFilter application."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    feeds: Mapped[List["Feed"]] = relationship("Feed", back_populates="user")
    filter_rules: Mapped[List["FilterRule"]] = relationship("FilterRule", back_populates="user")


class Feed(Base):
    """RSS feed model."""

    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    original_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="feeds")
    episodes: Mapped[List["Episode"]] = relationship("Episode", back_populates="feed")


class Episode(Base):
    """Episode model for podcast episodes."""

    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    feed_id: Mapped[int] = mapped_column(ForeignKey("feeds.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    guid: Mapped[str] = mapped_column(String(500), nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(500))
    enclosure_url: Mapped[Optional[str]] = mapped_column(String(500))
    enclosure_type: Mapped[Optional[str]] = mapped_column(String(100))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_filtered: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    feed: Mapped["Feed"] = relationship("Feed", back_populates="episodes")


class FilterRule(Base):
    """Filter rule model for episode filtering."""

    __tablename__ = "filter_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    feed_id: Mapped[Optional[int]] = mapped_column(ForeignKey("feeds.id"))  # None means applies to all feeds
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'title_contains', 'title_regex', 'description_contains'
    pattern: Mapped[str] = mapped_column(String(500), nullable=False)
    action: Mapped[str] = mapped_column(String(20), default="exclude")  # 'exclude' or 'include'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="filter_rules")