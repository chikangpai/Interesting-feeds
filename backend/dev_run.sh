#!/usr/bin/env bash
# Dev helper: wipe DB, repopulate, and start API with auto-reload.
# Usage:   ./backend/dev.sh [--port 8000]

set -euo pipefail

PORT=${1:-8000}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧹 Cleaning database…"
python clean_db.py --nuke 2>/dev/null || true

echo "📥 Fetching feeds…"
python feeder.py

echo "🚀 Starting API on http://127.0.0.1:${PORT} (reload enabled)"
exec uvicorn api.latest:app --reload --port "${PORT}" 