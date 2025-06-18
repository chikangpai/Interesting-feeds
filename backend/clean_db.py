#!/usr/bin/env python3
"""
Utility: wipe the backend/content.db before re-running feeder.py.

Usage
-----
$ python backend/clean_db.py           # delete all rows (keeps schema)
$ python backend/clean_db.py --nuke    # delete the entire DB file
"""
import os, argparse, sqlite3, sys

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "content.db")

parser = argparse.ArgumentParser(description="Clean the RSS articles database.")
parser.add_argument("--nuke", action="store_true",
                    help="Remove the entire content.db file instead of just clearing rows.")
args = parser.parse_args()

if not os.path.exists(DB_PATH):
    print("📂 No content.db found – nothing to clean.")
    sys.exit(0)

if args.nuke:
    os.remove(DB_PATH)
    print("💥 content.db removed. Re-run feeder.py to recreate and repopulate.")
else:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM articles")
        conn.commit()
    print("🧹 All rows deleted from the articles table. Re-run feeder.py to repopulate.") 