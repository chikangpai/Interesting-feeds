#!/usr/bin/env python3
"""
Shared feed utilities.

• FEEDS dictionary is defined in one place.
• `refresh_feeds(db_path)` populates/updates the SQLite database.
• Can be run directly: `python backend/feeds.py` to refresh backend/content.db.
"""
from __future__ import annotations

import os
import logging
import sqlite3
import textwrap
import traceback
from datetime import datetime
import html, re

import feedparser
import requests
from bs4 import BeautifulSoup  # relies on beautifulsoup4 dependency

# ---------------------------------------------------------------------------
# RSS/Atom feeds to ingest – edit in ONE PLACE only.
# ---------------------------------------------------------------------------
FEEDS: dict[str, str] = {
    "wip_podcast":   "https://feeds.transistor.fm/works-in-progress-podcast",
    "wip_books":     "https://books.worksinprogress.co/feeds/latest-revisions.xml",
    "lesswrong":     "https://www.lesswrong.com/feed.xml",
    "paul_graham":   "https://filipesilva.github.io/paulgraham-rss/feed.rss",
    "sam+altman":     "http://blog.samaltman.com/posts.atom",
    "sheracaolity":  "https://sheracaolity.ghost.io/rss/",
    # "nature":        "https://www.nature.com/nature.rss",
    # "science":       "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
    #"wip_notes":     "https://notes.worksinprogress.co/feed",
    #"arxiv_ai":      "http://export.arxiv.org/rss/cs.AI",
    "trenton_bricken":      "https://www.trentonbricken.com/index.xml",
    "marginal_revolution":  "https://feeds.feedblitz.com/MarginalRevolution",
    "yt_deep_dives":        "https://www.youtube.com/feeds/videos.xml?playlist_id=PLS01nW3RtgorL3AW8REU9nGkzhvtn6Egn",
    "yt_ai_fundamentals":   "https://www.youtube.com/feeds/videos.xml?playlist_id=PLVVTN-yNn8rvEwlY8ClxDUWeVPVfdifYj",
    "yt_ml_course":         "https://www.youtube.com/feeds/videos.xml?playlist_id=PLJV_el3uVTsNZEFAdQsDeOdzAaHTca2Gi",
}

TAG_RE = re.compile(r"<[^>]+>")
SNIPPET_CHARS = 280

def _html_to_text(raw_html: str) -> str:
    """Return plain-text version of an HTML fragment suitable for previews."""
    txt = html.unescape(raw_html or "")
    # quick sanitation – strip script/style blocks
    txt = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", txt)
    # use BeautifulSoup to get text (handles entities, nested tags)
    return BeautifulSoup(txt, "html.parser").get_text(separator=" ").strip()

# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def refresh_feeds(db_path: str, keep_latest: int = 1000) -> None:
    """Fetch all feeds and update *db_path* SQLite database.

    Creates the `articles` table if it does not yet exist and keeps only the
    *keep_latest* most–recent articles overall.
    """

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    with sqlite3.connect(db_path) as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS articles(
                id INTEGER PRIMARY KEY,
                source TEXT,
                title TEXT,
                link TEXT UNIQUE,
                published DATETIME,
                summary TEXT
            )"""
        )

        for src, url in FEEDS.items():
            try:
                resp = requests.get(
                    url,
                    timeout=10,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; InterestingFeeds/1.0)"},
                )
                resp.raise_for_status()
                d = feedparser.parse(resp.content)

                if not d.entries:
                    logging.warning("⚠️  %s: nothing parsed from %s", src, url)
                    continue

                for e in d.entries:
                    # broader timestamp support
                    ts = (
                        e.get("published_parsed")
                        or e.get("updated_parsed")
                        or e.get("dc_date")
                        or e.get("created_parsed")
                    )
                    dt = datetime(*ts[:6]) if ts else datetime.utcnow()

                    # Prefer full content (Ghost) then summary
                    if e.get("content"):
                        raw_html = e.content[0].value
                    else:
                        raw_html = e.get("summary", "")

                    plain = _html_to_text(raw_html)
                    summary = (
                        plain[:SNIPPET_CHARS] + "…" if len(plain) > SNIPPET_CHARS else plain
                    )

                    db.execute(
                        """INSERT OR IGNORE INTO articles
                            (source, title, link, published, summary)
                            VALUES (?,?,?,?,?)""",
                        (src, e.get("title", "").strip(), e.link, dt, summary),
                    )
            except Exception as exc:
                logging.error("RSS error for %s → %s", url, exc)
                logging.debug(traceback.format_exc())

        # Keep only the latest N items
        db.execute(
            "DELETE FROM articles WHERE id NOT IN (SELECT id FROM articles ORDER BY published DESC LIMIT ?)",
            (keep_latest,),
        )
        db.commit()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
    DB_PATH = os.path.join(ROOT_DIR, "content.db")
    refresh_feeds(DB_PATH)
    
    # Also refresh local files
    try:
        from local_files import refresh_local_files
        refresh_local_files(DB_PATH)
    except ImportError:
        print("⚠️  local_files module not available")
    
    print("✅ Feeds refreshed →", DB_PATH) 