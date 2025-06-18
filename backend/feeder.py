#!/usr/bin/env python3
"""Command–line helper to populate backend/content.db.
Run:  python backend/feeder.py
This delegates to feeds.refresh_feeds so the logic lives in one place.
"""
import os
from feeds import refresh_feeds

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "content.db")

if __name__ == "__main__":
    refresh_feeds(DB_PATH)
    print("✅ Feeds refreshed via feeder.py →", DB_PATH) 