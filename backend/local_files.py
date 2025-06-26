#!/usr/bin/env python3
"""
Local files integration for Interesting-feeds
Scans local directories for PDFs, EPUBs, and other documents
"""
import os
import sqlite3
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Dict
import hashlib

# Directories to scan for files - Add more folders here
LOCAL_FILES_DIRS = {
    "Research Papers": "/Users/brandonpai/Desktop/Research paper",
    "Books": "/Users/brandonpai/Desktop/Books",
    "AI papers": "/Users/brandonpai/Desktop/AI papers",
    "Exploratory-pdfs": "/Users/brandonpai/Desktop/Exploratory-pdfs",  # Directory doesn't exist yet
}

# Supported file types
SUPPORTED_EXTENSIONS = {'.pdf', '.epub', '.docx', '.doc', '.txt', '.md'}

def get_file_hash(file_path: str) -> str:
    """Generate a hash for the file to use as unique identifier"""
    return hashlib.md5(file_path.encode()).hexdigest()

def get_file_metadata(file_path: Path, folder_name: str) -> Dict:
    """Extract metadata from a file"""
    stat = file_path.stat()
    
    # Use filename as title, remove extension
    title = file_path.stem
    
    # Try to make title more readable
    title = title.replace('_', ' ').replace('-', ' ')
    title = ' '.join(word.capitalize() for word in title.split())
    
    # File info
    file_size = stat.st_size
    modified_time = datetime.fromtimestamp(stat.st_mtime)
    
    # Create a summary with file info and folder
    size_mb = file_size / (1024 * 1024)
    file_type = file_path.suffix.upper()
    summary = f"{file_type} file ({size_mb:.1f} MB) from {folder_name} - Modified: {modified_time.strftime('%Y-%m-%d')}"
    
    return {
        'title': title,
        'file_path': str(file_path.absolute()),
        'file_hash': get_file_hash(str(file_path.absolute())),
        'summary': summary,
        'modified_time': modified_time,
        'file_size': file_size,
        'file_type': file_path.suffix,
        'folder_name': folder_name
    }

def scan_local_files(directory: str, folder_name: str) -> List[Dict]:
    """Scan directory for supported files and return metadata"""
    if not os.path.exists(directory):
        print(f"⚠️  Directory not found: {directory}")
        return []
    
    files = []
    directory_path = Path(directory)
    
    for file_path in directory_path.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                metadata = get_file_metadata(file_path, folder_name)
                files.append(metadata)
            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")
    
    return files

def refresh_local_files(content_db_path: str):
    """Scan local files from all directories and update the database"""
    all_files = []
    
    for folder_name, directory in LOCAL_FILES_DIRS.items():
        print(f"📁 Scanning {folder_name} files in: {directory}")
        files = scan_local_files(directory, folder_name)
        all_files.extend(files)
        print(f"📁 Found {len(files)} files in {folder_name}")
    
    if not all_files:
        print("📁 No local files found in any directory")
        return
    
    print(f"📁 Total found: {len(all_files)} local files")
    
    with sqlite3.connect(content_db_path) as conn:
        # Create a table for local files if it doesn't exist
        conn.execute("""
            CREATE TABLE IF NOT EXISTS local_files (
                id INTEGER PRIMARY KEY,
                file_hash TEXT UNIQUE,
                file_path TEXT,
                title TEXT,
                file_type TEXT,
                file_size INTEGER,
                modified_time DATETIME,
                folder_name TEXT
            )
        """)
        
        # Clear existing local file entries from articles table
        conn.execute("DELETE FROM articles WHERE source LIKE '%local file)'")
        
        # Insert files into both tables
        for file_info in all_files:
            # Create source name like "Research Papers(local file)"
            source_name = f"{file_info['folder_name']}(local file)"
            
            # Insert into local_files table for file serving
            conn.execute("""
                INSERT OR REPLACE INTO local_files 
                (file_hash, file_path, title, file_type, file_size, modified_time, folder_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                file_info['file_hash'],
                file_info['file_path'],
                file_info['title'],
                file_info['file_type'],
                file_info['file_size'],
                file_info['modified_time'],
                file_info['folder_name']
            ))
            
            # Insert into articles table for feed display
            # Use a special URL format that our backend can handle
            file_url = f"/api/files/{file_info['file_hash']}"
            
            conn.execute("""
                INSERT INTO articles (source, title, link, published, summary)
                VALUES (?, ?, ?, ?, ?)
            """, (
                source_name,
                file_info['title'],
                file_url,
                file_info['modified_time'],
                file_info['summary']
            ))
        
        conn.commit()
        print(f"✅ Added {len(all_files)} local files to database")

def get_file_by_hash(content_db_path: str, file_hash: str) -> Tuple[str, str]:
    """Get file path and type by hash"""
    with sqlite3.connect(content_db_path) as conn:
        conn.row_factory = sqlite3.Row
        result = conn.execute(
            "SELECT file_path, file_type FROM local_files WHERE file_hash = ?",
            (file_hash,)
        ).fetchone()
        
        if result:
            return result['file_path'], result['file_type']
        return None, None

if __name__ == "__main__":
    # Test the scanner
    for folder_name, directory in LOCAL_FILES_DIRS.items():
        print(f"\n=== {folder_name} ===")
        files = scan_local_files(directory, folder_name)
        for file_info in files[:3]:  # Show first 3 files per folder
            print(f"📄 {file_info['title']}")
            print(f"   Path: {file_info['file_path']}")
            print(f"   Summary: {file_info['summary']}")
            print() 