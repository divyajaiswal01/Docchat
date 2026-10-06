# rules.md — Project Rules & Guardrails

## What to Use

**Backend**
- FastAPI for the API layer (async, built-in validation via Pydantic)
- `pdfplumber` for PDF text extraction (keeps page number metadata — needed for citations)
- Chroma for vector storage (local, no infra)
- Groq API for answer generation (free tier)
- Sentence-Transformers (local, free) for embeddings
- `python-dotenv` for environment variables
- Pydantic models for every request/response (no raw dicts)

**Frontend**
- React functional components + hooks only (no class components)
- Tailwind for styling (no custom CSS files unless unavoidable)
- Fetch or Axios for API calls, wrapped in a single `api.js` service file (not scattered everywhere)

**General**
- Git from day one, with meaningful commit messages
- `.env` for all secrets — never hardcoded keys
- Logging (even just `print`/basic logger) on every backend request for debugging

## What to Avoid
- ❌ No hardcoded API keys or secrets in source files
- ❌ No giant single-file backend (`main.py` with everything in it) — split by responsibility
- ❌ No skipping error handling "for now" — build it in from the start, not bolted on later
- ❌ No unbounded LLM calls — always set `max_tokens` and handle timeout/failure
- ❌ No sending the entire raw document to the LLM on every question (defeats the purpose of RAG, wastes tokens/cost)
- ❌ No storing raw uploaded files long-term (privacy + storage bloat) — delete after processing unless the user explicitly wants persistence
- ❌ No class components in React, no prop-drilling more than 2 levels (use context if needed)
- ❌ No committing `.env`, `node_modules`, or `__pycache__` to git

## Libraries — Allowed List
- Backend: `fastapi`, `uvicorn`, `pdfplumber`, `chromadb`, `python-dotenv`, `pydantic`, `groq` (SDK), `sentence-transformers`
- Frontend: `react`, `react-dom`, `tailwindcss`, `axios`
- Testing: `pytest` (backend), `vitest` (frontend) — optional but recommended for portfolio credibility

## Error Handling Standards
- Every API endpoint returns a consistent error shape: `{ "error": true, "message": "..." }`
- File upload: validate type (PDF only in v1) and size (cap at ~10MB) before processing
- LLM call failures: retry once, then return a graceful "couldn't generate an answer" message — never let the app crash or hang silently
- Empty/unparseable PDFs: detect early and tell the user clearly, don't send empty context to the LLM

## Boundaries for AI (when using Claude/Cursor/Copilot to help build this)
- AI can scaffold boilerplate (routes, components, config files) — review before accepting
- AI should NOT be trusted to pick security-sensitive defaults (CORS settings, auth, secret handling) without you double-checking
- Always ask AI to explain *why* it made a non-trivial architectural choice — don't paste code you don't understand into the project
- Don't let AI silently add new dependencies — check `requirements.txt`/`package.json` diffs
- Treat AI output as a first draft, not a final answer — this is especially important since this is a job-hunting portfolio piece; you need to be able to explain every line in an interview
