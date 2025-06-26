#!/usr/bin/env python3
"""
Local feeds integration for Interesting-feeds
Handles local data sources like Onebird.net alongside RSS feeds
"""
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Tuple

def get_local_sources() -> Dict[str, str]:
    """Define local data sources"""
    return {
        "onebird": "path/to/onebird.sqlite",  # Update with actual path
        # Add more local sources here
    }

def fetch_onebird_articles(db_path: str, limit: int = 50) -> List[Tuple]:
    """Fetch articles from Onebird database"""
    if not os.path.exists(db_path):
        return []
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            # Query based on actual onebird schema: title_tc, url, content_tc, date
            cursor.execute("""
                SELECT title_tc, url, content_tc, date 
                FROM posts 
                ORDER BY date DESC 
                LIMIT ?
            """, (limit,))
            return cursor.fetchall()
        except sqlite3.OperationalError as e:
            print(f"⚠️  Onebird table schema error: {e}")
            return []

def refresh_local_sources(content_db_path: str):
    """Add local sources to the main content database"""
    local_sources = get_local_sources()
    
    with sqlite3.connect(content_db_path) as conn:
        for source_name, source_path in local_sources.items():
            if source_name == "onebird":
                articles = fetch_onebird_articles(source_path)
                for article in articles:
                    title_tc, url, content_tc, date = article
                    # Skip if any required field is empty
                    if not title_tc or not url:
                        continue
                        
                    # Convert content to summary (match existing format)
                    content_text = content_tc or ""
                    summary = content_text[:280] + "..." if len(content_text) > 280 else content_text
                    
                    conn.execute(
                        """INSERT OR IGNORE INTO articles 
                           (source, title, link, published, summary) 
                           VALUES (?, ?, ?, ?, ?)""",
                        (source_name, title_tc, url, date, summary)
                    )
        conn.commit()

# Integration with existing feeds.py
def refresh_all_feeds(db_path: str):
    """Refresh both RSS feeds and local sources"""
    # Import and call existing refresh_feeds
    from feeds import refresh_feeds
    refresh_feeds(db_path)
    
    # Add local sources
    refresh_local_sources(db_path)
    print("✅ Refreshed RSS feeds and local sources") 