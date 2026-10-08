# DocChat

Upload a PDF, ask it questions, get answers grounded in the document text —
streamed in as they're generated, with a page citation underneath, backed
by persistent storage and a test suite.

**Quick start:** get a free [Groq API key](https://console.groq.com/keys) →
run the backend → run the frontend → open `localhost:5173`. Full steps below.

This is the **Phase 5** build — functionally complete, UX-polished, and
locally runnable end to end. See `phases.md` for what's left (deployment).

Planning docs for this project: `PRD.md`, `architecture.md`, `rules.md`, `phases.md`.

## What Phase 5 adds on top of Phase 4
- **A real landing screen** — a "how it works" 3-step explainer instead of
  a bare upload box, and mobile-responsive layout throughout
- **Better loading/empty states** — a spinner while a PDF is being read, a
  friendlier empty-chat prompt with an example question
- **Usage limits** — each uploaded document is capped at 20 questions
  (`services/usage_limiter.py`), with the remaining count shown live in the
  chat header so it's never a surprise. This exists to protect your free
  Groq rate limit from runaway usage, not as a product restriction
- **Design decisions documented below**, so a stranger reading only this
  README understands not just *how* to run the project but *why* it's built
  this way

## What Phase 4 added on top of Phase 3
- **Persistent document metadata** — SQLite (`db/database.py`) replaced the
  in-memory dict, so restarting the backend no longer orphans documents
  whose chunks are still sitting in `chroma_data/`
- **Request logging** — every request logs its method, path, status code,
  and duration (see `main.py`)
- **A real test suite** — `backend/tests/` covers chunking, retrieval, and
  metadata persistence (12 tests). Run with `pytest` from the `backend/` folder

## What Phase 3 added on top of Phase 2
- Answers now **stream in token by token** via Server-Sent Events, instead
  of waiting for the full response
- Each answer shows a **"Source: page X" citation**, taken from which
  retrieved chunks actually informed the answer
- The `/chat` endpoint changed from a single JSON response to a streaming
  response — see `routes/chat.py` and `frontend/src/api.js` (`streamAnswer`)
  if you want to see how the SSE protocol between them works

## What Phase 2 does (still true)
- Upload a PDF → text is extracted **per page**
- Each page is split into overlapping chunks (~2000 chars each)
- Chunks are embedded locally (fastembed / ONNX, free, no API) and
  stored in Chroma, a local vector database
- Ask a question → the question is embedded, the most relevant chunks are
  retrieved, and only those (not the whole document) go to the LLM (Groq)

## Setup

### 1. Get a free Groq API key
1. Go to https://console.groq.com and sign up (no credit card needed)
2. Go to **API Keys** → **Create API Key**
3. Copy the key — you'll paste it into `.env` in the next step

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste your GROQ_API_KEY
uvicorn main:app --reload --port 8000
```
> First run note: the first time you upload a document, the embedding model
> (~90MB) downloads automatically into `backend/model_cache/` — this only
> happens once, after that it's cached locally.
Backend runs at `http://localhost:8000`. Check `http://localhost:8000/health`.

### 3. Frontend
In a new terminal:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Frontend runs at `http://localhost:5173`.

### 4. Run the tests (optional but recommended)
With the venv active, from the `backend` folder:
```bash
pytest
```
These tests mock out the embedding model, so they run in a couple seconds
without needing the real embedding model downloaded or a Groq API key.

### 5. Try it
Open `http://localhost:5173`, upload a short PDF, and ask it a question.

## Troubleshooting

**"model does not exist or you do not have access to it" (404 from Groq)**
Model availability can vary slightly by account. Check which models your key
can actually use:
```bash
curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer YOUR_GROQ_API_KEY"
```
Then set `MODEL_NAME` in `backend/services/llm.py` to an exact ID from that list.
Model availability varies by account — the default here (`openai/gpt-oss-20b`)
was confirmed working for this project, but always check your own account's
list if you hit a 404.

**`TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`**
A newer `httpx` was installed than the `groq` SDK expects. Fix:
```bash
pip install -r requirements.txt --force-reinstall
```

## Post-Phase 5 fix: Markdown rendering
Groq sometimes answers with Markdown — bold text, bullet lists, and tables
(e.g. when asked to compare things). The chat bubble was rendering that as
raw text (literal `**` and `|` characters) instead of formatted output.
Fixed by rendering assistant messages through `react-markdown` +
`remark-gfm` (for table support) in `MessageBubble.jsx`. User messages and
error text stay plain — no need to parse Markdown from typed questions.
**This adds new frontend dependencies — run `npm install` again.**

## Design decisions (and why)

| Decision | Why |
|---|---|
| Groq instead of OpenAI/Anthropic APIs | Free tier, no credit card required — this was a hard constraint for the project |
| Local embeddings (fastembed/ONNX) instead of a cloud embeddings API | Groq doesn't offer one, and this avoids adding a second paid/rate-limited dependency |
| fastembed instead of sentence-transformers/PyTorch | Same all-MiniLM-L6-v2 model, but PyTorch alone needed more RAM than Render's 512MB free tier — the first deploy was killed with an out-of-memory error. ONNX Runtime fits |
| Chroma instead of Pinecone/a hosted vector DB | Zero infrastructure — a local, file-based store is enough for a single-user project at this scale |
| SQLite instead of Postgres for metadata | One file, no server to run, more than sufficient for the amount and shape of data stored |
| Character-based chunking instead of a tokenizer | Avoids an extra dependency; "close enough" token estimates are fine for this use case |
| Retrieval (RAG) instead of sending the full document | The only way to handle long documents without hitting context-window limits or wasting tokens — see Phase 2 |
| Streaming (SSE) instead of a single JSON response | Doesn't change the answer, but removes the "frozen screen" wait — see Phase 3 |
| In-memory usage limiter instead of a persisted one | Question counts resetting on restart is an acceptable tradeoff; it's a cost guard, not a security boundary |

## Known limitations (Phase 5, by design)
- No OCR — scanned/image-only PDFs won't extract text
- Citations show which pages were *retrieved and sent to the LLM*, not a
  guarantee the model used every one of them in its final answer — good
  enough for this project, but worth knowing the difference
- If the connection drops mid-stream, the partial answer stays on screen
  with no retry button yet
- Usage limits are per-process (in-memory) — they reset if the backend
  restarts, same tradeoff as everything in `services/usage_limiter.py`
- Not yet deployed anywhere — runs locally only until Phase 6

These are addressed in later phases (or are accepted tradeoffs), not bugs.

## Project structure

```
docchat/
├── PRD.md / architecture.md / rules.md / phases.md   # planning docs
├── backend/
│   ├── main.py                 # FastAPI app, logging middleware, DB init
│   ├── config.py                # all tunable constants in one place
│   ├── store.py                 # thin wrapper over db/database.py
│   ├── db/
│   │   └── database.py          # SQLite — document metadata, survives restarts
│   ├── routes/
│   │   ├── upload.py
│   │   └── chat.py               # SSE streaming + citations + usage limit
│   ├── services/
│   │   ├── pdf_parser.py
│   │   ├── chunker.py
│   │   ├── embeddings.py         # local, free
│   │   ├── vector_store.py       # Chroma wrapper
│   │   ├── llm.py                 # Groq, streaming + non-streaming
│   │   └── usage_limiter.py       # Phase 5
│   └── tests/                    # pytest, 15 tests, embeddings mocked
└── frontend/
    └── src/
        ├── App.jsx                # landing screen + how-it-works
        ├── api.js                 # upload + SSE streaming client
        └── components/
            ├── UploadBox.jsx
            ├── ChatWindow.jsx      # streaming, citations, usage display
            └── MessageBubble.jsx
```
