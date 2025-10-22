"""RSS feed parsing and OPML handling utilities."""

import re
from datetime import datetime
from typing import Dict, List, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

import feedparser
import httpx
import opml
from opml import from_string


class FeedParser:
    """RSS feed parser."""

    @staticmethod
    async def fetch_and_parse_feed(url: str) -> Dict:
        """Fetch and parse an RSS feed from URL."""
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()

        feed_data = feedparser.parse(response.content)

        if feed_data.bozo:
            raise ValueError(f"Invalid RSS feed: {feed_data.bozo_exception}")

        return {
            "title": feed_data.feed.get("title", "Unknown Feed"),
            "description": feed_data.feed.get("description", ""),
            "link": feed_data.feed.get("link", ""),
            "episodes": [
                {
                    "title": entry.get("title", "Untitled Episode"),
                    "description": entry.get("description", ""),
                    "guid": entry.get("id", entry.get("link", "")),
                    "link": entry.get("link", ""),
                    "enclosure_url": entry.enclosures[0].href if entry.enclosures else None,
                    "enclosure_type": entry.enclosures[0].type if entry.enclosures else None,
                    "published_at": datetime(*entry.published_parsed[:6])
                    if hasattr(entry, "published_parsed") and entry.published_parsed
                    else None,
                }
                for entry in feed_data.entries
            ],
        }


class OPMLHandler:
    """OPML file handler."""

    @staticmethod
    def parse_opml(opml_content: str) -> List[Dict[str, str]]:
        """Parse OPML content and extract feed URLs."""
        try:
            opml_doc = from_string(opml_content)
            feeds = []

            def extract_feeds(outline):
                if hasattr(outline, "xmlUrl") and outline.xmlUrl:
                    feeds.append(
                        {
                            "title": getattr(outline, "title", getattr(outline, "text", "Unknown Feed")),
                            "url": outline.xmlUrl,
                            "description": getattr(outline, "description", ""),
                        }
                    )

                if hasattr(outline, "children"):
                    for child in outline.children:
                        extract_feeds(child)
                elif hasattr(outline, "_children"):
                    for child in outline._children:
                        extract_feeds(child)

            for outline in opml_doc.outline:
                extract_feeds(outline)

            return feeds
        except Exception as e:
            raise ValueError(f"Invalid OPML file: {e}")

    @staticmethod
    def generate_opml(feeds: List[Dict[str, str]], title: str = "PodFilter Feeds") -> str:
        """Generate OPML content from feed list."""
        opml = Element("opml", version="2.0")
        head = SubElement(opml, "head")
        title_elem = SubElement(head, "title")
        title_elem.text = title

        body = SubElement(opml, "body")

        for feed in feeds:
            outline = SubElement(
                body,
                "outline",
                text=feed.get("title", "Unknown Feed"),
                title=feed.get("title", "Unknown Feed"),
                type="rss",
                xmlUrl=feed["url"],
            )
            if feed.get("description"):
                outline.set("description", feed["description"])

        return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(opml, encoding="unicode")


class FilterEngine:
    """Episode filtering engine."""

    @staticmethod
    def apply_filters(episodes: List[Dict], filter_rules: List[Dict]) -> List[Dict]:
        """Apply filter rules to episodes."""
        filtered_episodes = []

        for episode in episodes:
            should_include = True

            for rule in filter_rules:
                if not rule.get("is_active", True):
                    continue

                rule_type = rule["rule_type"]
                pattern = rule["pattern"]
                action = rule.get("action", "exclude")

                matches = False

                if rule_type == "title_contains":
                    matches = pattern.lower() in episode.get("title", "").lower()
                elif rule_type == "title_regex":
                    matches = bool(re.search(pattern, episode.get("title", ""), re.IGNORECASE))
                elif rule_type == "description_contains":
                    matches = pattern.lower() in episode.get("description", "").lower()

                if matches:
                    if action == "exclude":
                        should_include = False
                        break
                    elif action == "include":
                        should_include = True

            if should_include:
                filtered_episodes.append(episode)

        return filtered_episodes


class RSSGenerator:
    """RSS feed generator."""

    @staticmethod
    def generate_rss(feed_info: Dict, episodes: List[Dict], base_url: str = "http://localhost:8000") -> str:
        """Generate RSS XML from feed info and episodes."""
        rss = Element("rss", version="2.0")
        channel = SubElement(rss, "channel")

        # Channel info
        title = SubElement(channel, "title")
        title.text = feed_info.get("title", "Unknown Feed")

        description = SubElement(channel, "description")
        description.text = feed_info.get("description", "")

        link = SubElement(channel, "link")
        link.text = feed_info.get("link", base_url)

        # Episodes
        for episode in episodes:
            item = SubElement(channel, "item")

            title = SubElement(item, "title")
            title.text = episode.get("title", "Untitled Episode")

            if episode.get("description"):
                desc = SubElement(item, "description")
                desc.text = episode["description"]

            if episode.get("link"):
                link = SubElement(item, "link")
                link.text = episode["link"]

            if episode.get("guid"):
                guid = SubElement(item, "guid")
                guid.text = episode["guid"]

            if episode.get("enclosure_url"):
                enclosure = SubElement(
                    item, "enclosure", url=episode["enclosure_url"], type=episode.get("enclosure_type", "audio/mpeg")
                )

            if episode.get("published_at"):
                pub_date = SubElement(item, "pubDate")
                pub_date.text = episode["published_at"].strftime("%a, %d %b %Y %H:%M:%S +0000")

        return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(rss, encoding="unicode")
