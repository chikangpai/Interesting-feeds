import os
import sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# The SQLite database sits one directory above this file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "content.db")

@app.get("/latest")
def latest(limit: int = 50):
    """Return the most recent articles.

    The query is identical to the previous api.py implementation; we only
    changed the path resolution so it still points at the same
    `content.db` even after moving this file to backend/api/.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM articles ORDER BY published DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows] 