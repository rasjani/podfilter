"""
Unit tests covering utility helpers such as OPML handling, filtering, and RSS generation.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from podfilter.utils import FilterEngine, OPMLHandler, RSSGenerator


def test_filter_engine_excludes_matching_episode() -> None:
  """Episodes matching an exclude rule should be dropped."""
  episodes = [
    {"title": "Learn Python", "description": "Deep dive"},
    {"title": "Gardening Tips", "description": "Plants"},
  ]
  rules = [
    {"rule_type": "title_contains", "pattern": "python", "action": "exclude", "is_active": True},
  ]

  filtered = FilterEngine.apply_filters(episodes, rules)

  assert len(filtered) == 1
  assert filtered[0]["title"] == "Gardening Tips"


def test_filter_engine_include_rule_keeps_episode() -> None:
  """Include rules should allow content even after a match."""
  episodes = [
    {"title": "Weekly Roundup", "description": "All news"},
  ]
  rules = [
    {"rule_type": "title_contains", "pattern": "roundup", "action": "include", "is_active": True},
  ]

  filtered = FilterEngine.apply_filters(episodes, rules)

  assert filtered == episodes


def test_filter_engine_skips_inactive_rules() -> None:
  """Inactive rules must be ignored when filtering."""
  episodes = [{"title": "Episode Zero", "description": "Pilot"}]
  rules = [
    {"rule_type": "title_contains", "pattern": "episode", "action": "exclude", "is_active": False},
  ]

  filtered = FilterEngine.apply_filters(episodes, rules)

  assert filtered == episodes


def test_opml_handler_parse_returns_flat_list() -> None:
  """Parsing OPML should return feed metadata for nested outlines."""
  opml_content = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head><title>Subscriptions</title></head>
  <body>
    <outline text="Tech">
      <outline text="PodFilter" title="PodFilter Feed" xmlUrl="https://example.com/feed.xml" description="Tech pods" />
      <outline text="Another" xmlUrl="https://example.com/other.xml" />
    </outline>
  </body>
</opml>
"""

  feeds = OPMLHandler.parse_opml(opml_content)

  assert feeds == [
    {"title": "PodFilter Feed", "url": "https://example.com/feed.xml", "description": "Tech pods"},
    {"title": "Another", "url": "https://example.com/other.xml", "description": ""},
  ]


def test_opml_handler_parse_raises_for_invalid_input() -> None:
  """Invalid OPML content should raise a ValueError."""
  with pytest.raises(ValueError, match="Invalid OPML file"):
    OPMLHandler.parse_opml("<not-opml>")


def test_opml_handler_generate_contains_feeds() -> None:
  """Generated OPML should contain all provided feeds."""
  opml_xml = OPMLHandler.generate_opml(
    [
      {"title": "Feed One", "url": "https://example.com/one.xml", "description": "One"},
      {"title": "Feed Two", "url": "https://example.com/two.xml", "description": ""},
    ],
    title="My Feeds",
  )

  assert "<outline" in opml_xml
  assert "Feed One" in opml_xml
  assert "https://example.com/two.xml" in opml_xml
  assert "<title>My Feeds</title>" in opml_xml


def test_rss_generator_creates_rss_document() -> None:
  """RSS generation should emit expected channel and item elements."""
  published = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)  # noqa: UP017
  rss_xml = RSSGenerator.generate_rss(
    feed_info={"title": "PodFilter Feed", "description": "Filtered shows", "link": "https://example.com"},
    episodes=[
      {
        "title": "Episode One",
        "description": "Intro",
        "guid": "episode-1",
        "link": "https://example.com/episodes/1",
        "enclosure_url": "https://cdn.example.com/episodes/1.mp3",
        "enclosure_type": "audio/mpeg",
        "published_at": published,
      }
    ],
  )

  assert "<rss" in rss_xml
  assert "<title>PodFilter Feed</title>" in rss_xml
  assert "Episode One" in rss_xml
  assert "episode-1" in rss_xml
  assert "1.mp3" in rss_xml
  assert "Sun, 01 Jan 2023 12:00:00 +0000" in rss_xml
