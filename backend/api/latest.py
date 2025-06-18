import os, sqlite3, random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional

# Shared feed utilities
from feeds import refresh_feeds

app = FastAPI(root_path="/api/latest")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "content.db")

# refresh_feeds imported from feeds module; we'll wrap a convenience lambda with DB_PATH applied.
def _refresh_feeds_wrapper():
    refresh_feeds(DB_PATH)

# ---------------------------------------------------------------------------
# FastAPI startup/shutdown hooks to keep the scheduler alive
# ---------------------------------------------------------------------------

_scheduler: Optional[BackgroundScheduler] = None

@app.on_event("startup")
def _on_startup():
    global _scheduler
    _refresh_feeds_wrapper()  # initial population
    if not os.environ.get("VERCEL"):
        _scheduler = BackgroundScheduler()
        _scheduler.add_job(_refresh_feeds_wrapper, "interval", minutes=30, max_instances=1)
        _scheduler.start()

        # Ensure it is shut down properly on exit
        atexit.register(lambda: _scheduler.shutdown(wait=False) if _scheduler else None)

@app.get("/")
@app.get("/{limit}")
def latest(limit: int = 300, per_source: int = 20, refresh: bool = False):
    if refresh:
        _refresh_feeds_wrapper()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        if per_source:
            # Grab the most recent `per_source` items from each feed/source.
            rows = conn.execute(
                """
                SELECT * FROM (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY source ORDER BY published DESC) AS rn
                    FROM articles
                ) WHERE rn <= ?
                """,
                (per_source,)
            ).fetchall()
        else:
            # Fallback: simply take the latest `limit` rows overall.
            rows = conn.execute(
                "SELECT * FROM articles ORDER BY published DESC LIMIT ?", (limit,)
            ).fetchall()

    # Convert to dicts first so we can shuffle easily
    items = [dict(r) for r in rows]
    random.shuffle(items)
    # Trim the shuffled list to `limit` if that constraint is still desired.
    return items[:limit] if limit else items

# When running locally (e.g. via `vercel dev` or `uvicorn`), expose the same
# handler under the full production path so the frontend can always request
# `<host>/api/latest`.
# This has no effect on Vercel production because that environment already
# prefixes the function with "/api/latest".
app.add_api_route("/api/latest", latest, methods=["GET"])
app.add_api_route("/api/latest/{limit}", latest, methods=["GET"])
