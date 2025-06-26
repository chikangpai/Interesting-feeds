#!/usr/bin/env python3
"""
Manual script to scan and add local files to the database
Usage: python backend/scan_files.py
"""
import os
from local_files import refresh_local_files

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DB_PATH = os.path.join(SCRIPT_DIR, "content.db")

if __name__ == "__main__":
    print("🔍 Scanning local files and adding to database...")
    refresh_local_files(DB_PATH)
    print("✅ Local files scan complete!") 