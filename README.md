# StudyAssistant AI

An AI-powered learning platform that helps students understand academic material, generate practice content, organize study sessions, and track academic progress.

## Status

Phase 0 — Project Foundation. Backend and frontend skeletons are running with a verified database connection. No application features exist yet.

Phase 1 — Authentication. Users can register, log in, and access protected routes with a JWT bearer token. Backend exposes `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me`. Frontend has login/register pages and a protected home page backed by a React auth context.

Phase 2 — User & Academic Profile. Every user has an academic profile (full name, academic level, institution, program, subjects, academic goals) created automatically on first access. Backend exposes `GET /api/v1/profile/me` and `PATCH /api/v1/profile/me`. Frontend has an editable profile page linked from the home page.

Phase 3 — Dashboard. The authenticated landing page is a real dashboard showing profile completion (computed server-side), quick actions, and honest empty states for recent activity, upcoming sessions, and weak areas — those sections will populate once quizzes, study sessions, and analytics exist in later phases.

Phase 4 — Subjects & Courses. Users can create, edit, and delete subjects, add and remove topics within each subject, and mark topics complete. Progress percentage is computed server-side from real completion state. Ownership is enforced on every subject/topic endpoint — a user can never see or modify another user's data. Navigation is now a shared top bar (Dashboard / Subjects / Profile) rather than per-page links.

Phase 5 — Document Management. Users can upload PDF and plain-text/markdown study materials (up to 20 MB), optionally tagged to a subject. Text is extracted synchronously on upload — PDFs via `pypdf`, text/markdown via UTF-8/Latin-1 decoding — and stored for future use by the AI Tutor and RAG phases. Processing failures (e.g. scanned PDFs with no embedded text) are tracked honestly rather than silently ignored. Files are stored on local disk under `UPLOAD_DIR`, scoped per document with UUID-based filenames; original filenames are preserved only as display metadata.

Phase 6 — AI Tutor. Users can chat with a local AI tutor running via Ollama (`llama3.2:3b` by default — no cloud API, no API key). Conversations can be scoped to a subject for context, support adjustable explanation levels (beginner/intermediate/advanced), and a Socratic mode that guides with questions instead of direct answers. The AI layer is abstracted behind a generic provider interface so the backend model could be swapped later. Requires Ollama installed and running locally — see setup docs.

Phase 7 — RAG Knowledge System. Uploaded documents are automatically chunked and embedded (via Ollama's `all-minilm` model) into PostgreSQL using the pgvector extension — no separate vector database. When chatting with the AI tutor, the student's own document chunks are searched for relevance and, when found, injected into the AI's context with source attribution; the assistant's reply records which documents it drew from. Irrelevant documents are correctly excluded rather than forced into every answer. Indexing failures (e.g. Ollama unavailable at upload time) are tracked honestly and can be retried per-document.

Phase 8 — Quiz Generator. Users can generate AI-created quizzes (multiple choice, true/false, short answer) at a chosen difficulty, optionally scoped to a subject and grounded in that subject's indexed documents via the RAG system. The AI is prompted for strict JSON output (Ollama's JSON mode) and every question is validated before storage — malformed or internally-inconsistent questions (e.g. a multiple-choice answer not matching its own options) are filtered out rather than trusted. Generated quizzes are reviewable with answers and explanations shown.

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