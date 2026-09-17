# StudyAssistant AI

An AI-powered learning platform that helps students understand academic material, generate practice content, organize study sessions, and track academic progress.

## Status

Live in production.

## Tech Stack

**Frontend:** React, TypeScript, Vite, Material UI, React Router, Axios, Recharts

**Backend:** Python, FastAPI, SQLAlchemy, Alembic, Pydantic, pytest

**Database:** PostgreSQL with pgvector (Neon in production, local Postgres in development)

**AI inference:** Ollama for local development; Google Gemini (with optional Groq fallback) in
production, selected via the `AI_PROVIDER` / `AI_FALLBACK_PROVIDER` settings — no code changes
required to switch

**Embeddings:** a local ONNX model (`all-MiniLM-L6-v2`, 384 dimensions) runs in-process via
`fastembed` for both development (the `ollama` embedding provider is also available) and
production (`onnx`), so the vector schema never changes regardless of provider

**File storage:** local disk in development; Supabase Storage in production, selected via
`STORAGE_BACKEND`

## Project Structure

StudyAssistantAI/
├── backend/ FastAPI application, SQLAlchemy models, Alembic migrations, Dockerfile
├── frontend/ React + TypeScript client, deployed to Vercel
└── docs/ Architecture and setup documentation

## Prerequisites

- Python 3.12
- Node.js 20+
- PostgreSQL 16 (running locally, with the `vector` extension enabled)
- Homebrew (macOS)
- Ollama (for local AI inference and embeddings) — see https://ollama.com



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

## License

MIT