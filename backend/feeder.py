#!/usr/bin/env python3
"""
Run with:  python backend/feeder.py    # or let GitHub-Actions call it
Creates/updates backend/content.db with the latest 300 items total.
"""
import os
from datetime import datetime
import textwrap, sqlite3, feedparser

FEEDS = {
    "wip_podcast":   "https://feeds.transistor.fm/works-in-progress-podcast",
    "wip_books":     "https://books.worksinprogress.co/feeds/latest-revisions.xml",
    "lesswrong":     "https://www.lesswrong.com/feed.xml",
    "paul_graham":   "https://www.aaronsw.com/2002/pgessays/index.rss",
    "sheracaolity":  "https://sheracaolity.ghost.io/rss/",
    "arxiv_ai":      "http://export.arxiv.org/rss/cs.AI",
    "nature":        "https://www.nature.com/nature.rss",
    "science":       "https://www.science.org/action/showFeed?type=etoc&feed=rss&jc=science",
}

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "content.db")
db = sqlite3.connect(DB_PATH)

db.execute("""CREATE TABLE IF NOT EXISTS articles(
    id INTEGER PRIMARY KEY,
    source TEXT, title TEXT, link TEXT UNIQUE,
    published DATETIME, summary TEXT)""")

for src, url in FEEDS.items():
    d = feedparser.parse(url)
    for e in d.entries:
        ts = e.get("published_parsed") or e.get("updated_parsed")
        dt = datetime(*ts[:6]) if ts else datetime.utcnow()
        summary = textwrap.shorten(e.get("summary",""), 280)
        db.execute("""INSERT OR IGNORE INTO articles
                      (source,title,link,published,summary)
                      VALUES (?,?,?,?,?)""",
                   (src, e.title, e.link, dt, summary))
db.execute("DELETE FROM articles WHERE id NOT IN "
           "(SELECT id FROM articles ORDER BY published DESC LIMIT 300)")
db.commit()
db.close() 