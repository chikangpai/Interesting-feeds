import os, sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api/latest")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "content.db")

@app.get("/")
@app.get("/{limit}")
def latest(limit: int = 50):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM articles ORDER BY published DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
