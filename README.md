# StudyAssistant AI

An AI-powered learning platform that helps students understand academic material, generate practice content, organize study sessions, and track academic progress.

## Status

🚧 In Development

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

## Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

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