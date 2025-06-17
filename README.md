# Interesting-feeds

A full-stack application that aggregates and displays interesting feeds from various sources.

## Tech Stack

-   **Frontend**: [Next.js](https://nextjs.org/), [React](https://react.dev/), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/)
-   **Backend**: [FastAPI](https://fastapi.tiangolo.com/), [Python](https://www.python.org/), [feedparser](https://pypi.org/project/feedparser/)

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

-   Node.js (v20 or later recommended)
-   Python (v3.8 or later recommended)
-   `pip`

### Installation & Running

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/your-username/Interesting-feeds.git
    cd Interesting-feeds
    ```

2.  **Backend Setup:**

    ```sh
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

3.  **Run Backend:**
    (Still in the `backend` directory)
    ```sh
    uvicorn api:app --reload
    ```
    The backend API will be available at `http://127.0.0.1:8000`.

4.  **Frontend Setup:**
    Open a new terminal.
    ```sh
    cd frontend
    npm install
    ```

5.  **Run Frontend:**
    (Still in the `frontend` directory)
    ```sh
    npm run dev
    ```
    The frontend development server will start, and you can view the application at `http://localhost:3000`.

---

Happy coding! 