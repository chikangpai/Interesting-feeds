# Interesting-feeds

*A personal "link newspaper" that scrapes RSS/blog sources into a lightweight backend and serves them through a modern Next.js UI.*

## Project overview

```
Interesting-feeds/
├── backend/         ← Python 3.11  · FastAPI  · SQLite
│   ├── feeder.py    · RSS/Atom feed scraper (writes to content.db)
│   ├── scan_files.py · local file scanner (indexes PDFs, docs, etc.)
│   ├── local_files.py · local file management utilities
│   ├── api/         · serverless endpoints (deployed on Vercel)
│   │   └── latest.py    · GET /api/latest – returns articles & files
│   │                    · GET /api/files/{hash} – serves local files
│   ├── content.db   · SQLite DB (RSS articles + local file metadata)
│   └── vercel.json  · tells Vercel CLI to run Uvicorn in dev
│
└── frontend/        ← Next.js 15  · TypeScript  · Tailwind CSS
    ├── app/page.tsx · SSR page that renders RSS + local files
    ├── globals.css  · Tailwind imports + base styles
    ├── vercel.json  · rewrite that proxies /api/* to backend in production
    └── …            · config, assets, etc.
```

### Data-flow in production
1. `cron` (or manual run) executes **`python backend/feeder.py`** – fetches feeds & writes to SQLite.
2. **`python backend/scan_files.py`** – scans local directories for files and updates the database.
3. FastAPI **`GET /api/latest`** reads `content.db` and returns JSON.
4. Next.js page **`frontend/app/page.tsx`** fetches that JSON on the server
   and streams rendered HTML to the browser.

## Local Files Integration

In addition to RSS feeds, the system supports integrating local files (PDFs, EPUBs, documents) as feed sources. This allows you to manage your research papers, books, and documents alongside your RSS articles.

### Features

- **Multiple directories**: Configure multiple local folders as separate feed sources
- **Folder-based naming**: Each directory becomes a named source (e.g., "Research Papers(local file)")
- **Supported file types**: `.pdf`, `.epub`, `.docx`, `.doc`, `.txt`, `.md`
- **In-browser viewing**: Files open inline in the browser (not as downloads)
- **Visual distinction**: Local files appear with 📄 icons and blue highlighting
- **Automatic scanning**: Files are indexed with metadata (title, date, size)

### Configuration

Edit `backend/local_files.py` to configure your local directories:

```python
LOCAL_FILES_DIRS = {
    "Research Papers": "/Users/brandonpai/Desktop/Research paper",
    "Books": "/Users/brandonpai/Desktop/Books",
    "AI papers": "/Users/brandonpai/Desktop/AI papers",
    "Exploratory-pdfs": "/Users/brandonpai/Desktop/Exploratory-pdfs",
}
```

### Usage

1. **Add files to your configured directories**
2. **Scan for new files**:
   ```bash
   cd backend
   python scan_files.py
   ```
3. **Files will appear in your feed with folder-based source names**
4. **Click files to view them inline in your browser**

Files are served through the API endpoint `/api/files/{file_hash}` with proper MIME types and security headers.

## Tech Stack

-   **Frontend**: [Next.js](https://nextjs.org/), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/)
-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [Python](https://www.python.org/), [feedparser](https://pypi.org/project/feedparser/)

## Getting Started

To run the stack you have **two options**. The first one mirrors the
exact Vercel production layout (recommended). The second one is the
classic Uvicorn + Next.js combo.

### 1. (DON'T!!) Vercel-style local dev (but currently under some error)
#### We should be able to use vercel dev, but we have some unexpected problems now. **
Specifically, the problem is that for backend we some how can only expose api to 8000, instead of 8000/api/latest, so the frontend cannot get the api properly. Will fix this soon. 

This relies on the Vercel CLI so you see the same behaviour locally and
in the cloud.

```bash
# Terminal 1 ──────────── backend
cd backend
vercel dev --listen 8000           # FastAPI ⇢ http://localhost:8000

# Terminal 2 ──────────── frontend
cd frontend
# tell the UI where the API lives
export FEEDS_API_URL=http://localhost:8000   # or echo > .env.local
vercel dev                                   # Next.js ⇢ http://localhost:3000
```

Browse to <http://localhost:3000>. The UI will fetch
`http://localhost:8000/api/latest` and render the articles.

### 2. Classic dev workflow

```bash
# Terminal 1 – backend
cd backend && uvicorn api.latest:app --reload --port 8000

# Terminal 2 – frontend
cd frontend && npm run dev       # defaults to http://localhost:3000
```



### Environment variables

| Scope      | File / location            | Notes                              |
|------------|---------------------------|------------------------------------|
| Frontend   | `frontend/.env.local`     | **Required** – `FEEDS_API_URL`     |
| Backend    | `backend/.env`            | Optional: `FEEDS_LIST`, secrets…   |
| Shared     | `.env` (repo root)        | Rarely used; keeps common values   |
| Example    | `*-example` files         | Template references – no secrets   |

### Deploying to Vercel

Both sub-projects are already linked to Vercel. Deploy via Git (push to
`main`) **or** manually:

```bash
# Backend – FastAPI
cd backend && vercel --prod

# Frontend – Next.js
cd frontend && vercel --prod
```

The live endpoints will be:

```
Backend  – https://my-feeds-api.vercel.app/api/latest
Frontend – https://my-feeds-web.vercel.app  (fetches the URL above)
```

## Connecting the front-end to the API

We implement the FastAPI service by copying the backend api deployment url into frontend's vercel project's environment variable

### Absolute URL via environment variable

```
frontend/app/page.tsx
const res = await fetch(`${process.env.FEEDS_API_URL}/api/latest`)
```

* **Local dev**  `frontend/.env.local`
  ```
  FEEDS_API_URL=http://localhost:8000
  ```
* **Vercel Preview / Production**  (Project → Settings → Environment Variables)
  ```
  FEEDS_API_URL=https://backend-chi-kangs-projects.vercel.app/     # Added at Vercel Deployment, Environment Variables.
  ```
No extra config files are needed. When you promote a new backend build the
alias, keeps pointing at the latest deployment, so
no code change is required.