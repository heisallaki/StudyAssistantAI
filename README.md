# StudyAssistant AI

An AI-powered learning platform that helps students understand academic material, generate practice content, organize study sessions, and track academic progress.

## Status

Phase 0 — Project Foundation. Backend and frontend skeletons are running with a verified database connection. No application features exist yet.

Phase 1 — Authentication. Users can register, log in, and access protected routes with a JWT bearer token. Backend exposes `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`. Frontend has login/register pages and a protected home page backed by a React auth context.

Phase 2 — User & Academic Profile. Every user has an academic profile (full name, academic level, institution, program, subjects, academic goals) created automatically on first access. Backend exposes `GET /api/v1/profile/me` and `PATCH /api/v1/profile/me`. Frontend has an editable profile page linked from the home page.

## Tech Stack

**Frontend:** React, TypeScript, Vite, Material UI, React Router, Axios, Recharts

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, Pydantic, pytest

**Database:** PostgreSQL

**AI:** Ollama (local inference), integrated in a later phase

## Project Structure

StudyAssistantAI/
├── backend/ FastAPI application, SQLAlchemy models, Alembic migrations
├── frontend/ React + TypeScript client
└── docs/ Architecture and setup documentation

## Prerequisites

- Python 3.12
- Node.js 20+
- PostgreSQL 16 (running locally)
- Homebrew (macOS)

## Backend Setup

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL` to your local Postgres credentials and `JWT_SECRET_KEY` to the output of:

```bash
openssl rand -hex 32
```

Run the API:

```bash
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`.

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The app is available at `http://localhost:5173`.

## Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

## Roadmap

Authentication, user profiles, dashboard, subjects, document management, AI tutor, RAG knowledge system, quiz generator and engine, flashcards, study planner, progress analytics, notifications, search, administration, security hardening, testing, performance, deployment, and the v1.0.0 release.

## License

MIT