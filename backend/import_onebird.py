#!/usr/bin/env python3
"""
Import Onebird.net data into content.db
Usage: python backend/import_onebird.py path/to/onebird.sqlite
"""
import sys
import sqlite3
import os
from datetime import datetime

def import_onebird_data(onebird_db_path: str, content_db_path: str):
    """Import data from onebird.sqlite into content.db"""
    
    if not os.path.exists(onebird_db_path):
        print(f"❌ Onebird database not found: {onebird_db_path}")
        return
    
    print(f"📥 Importing from: {onebird_db_path}")
    print(f"📤 Importing to: {content_db_path}")
    
    # Connect to both databases
    onebird_conn = sqlite3.connect(onebird_db_path)
    content_conn = sqlite3.connect(content_db_path)
    
    try:
        # First, let's see what tables exist in onebird.sqlite
        cursor = onebird_conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Tables in onebird.sqlite: {[t[0] for t in tables]}")
        
        # Query the onebird posts table
        cursor.execute("SELECT title_tc, url, content_tc, date FROM posts ORDER BY date DESC")
        rows = cursor.fetchall()
        
        if not rows:
            print("⚠️  No posts found in onebird.sqlite")
            return
        
        print(f"📋 Found {len(rows)} posts to import")
        
        # Import into content.db
        content_cursor = content_conn.cursor()
        imported_count = 0
        
        for row in rows:
            title_tc, url, content_tc, date = row
            
            # Skip if any required field is empty
            if not title_tc or not url:
                continue
                
            # Convert content to summary (truncate to 280 chars)
            content_text = content_tc or ""
            summary = content_text[:280] + "..." if len(content_text) > 280 else content_text
            
            # Convert date format if needed (onebird uses TEXT, content.db expects DATETIME)
            # Assuming date is in a reasonable format, SQLite will handle the conversion
            published_date = date or datetime.now().isoformat()
            
            try:
                content_cursor.execute(
                    "INSERT OR IGNORE INTO articles (source, title, link, published, summary) VALUES (?, ?, ?, ?, ?)",
                    ("onebird", title_tc, url, published_date, summary)
                )
                imported_count += 1
            except Exception as e:
                print(f"⚠️  Skipped article '{title_tc}': {e}")
        
        content_conn.commit()
        print(f"✅ Imported {imported_count} articles from Onebird")
        
    except Exception as e:
        print(f"❌ Error importing data: {e}")
    finally:
        onebird_conn.close()
        content_conn.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python import_onebird.py path/to/onebird.sqlite")
        sys.exit(1)
    
    onebird_db_path = sys.argv[1]
    script_dir = os.path.dirname(os.path.realpath(__file__))
    content_db_path = os.path.join(script_dir, "content.db")
    
    import_onebird_data(onebird_db_path, content_db_path)

if __name__ == "__main__":
    main() 