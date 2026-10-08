# phases.md — Build Phases

## Phase 1 — Bare-bones Q&A (no RAG yet) ✅ DONE
Goal: prove the end-to-end flow works before adding complexity.
- Set up FastAPI backend + React frontend skeleton
- Upload a PDF → extract full text with `pdfplumber`
- Send full extracted text + user question directly to Groq API (free tier)
- Display the answer in a simple chat UI (no streaming, no citations yet)
- **Done when:** you can upload a short PDF and get a relevant answer back

## Phase 2 — Real RAG (chunking + retrieval) ✅ DONE
Goal: make it scale to long documents and reduce token cost.
- Split per-page extracted text into ~2000-character overlapping chunks, page numbers attached
- Generate embeddings locally with fastembed (free, no API; originally sentence-transformers, swapped in Phase 6 to fit in 512MB RAM) for each chunk, store in Chroma
- On each question: embed the question, retrieve top-k (4) similar chunks
- Send only retrieved chunks (not the whole doc) + question to Groq
- **Done when:** a 50+ page PDF works, and retrieval returns the right chunk for a test question

## Phase 3 — Citations + Streaming ✅ DONE
Goal: make answers trustworthy and feel responsive.
- Return the page number/chunk source alongside the answer (via an SSE `sources` event, deduplicated and sorted)
- Display citation as "Source: page X" text under each answer in the chat UI
- Switch LLM call to streaming (Groq `stream=True`) via Server-Sent Events; render tokens as they arrive in the UI with a blinking cursor
- **Done when:** answers appear progressively and each one shows "Source: page X"

## Phase 4 — Robustness & Error Handling ✅ DONE
Goal: make it behave like a real product, not a demo script.
- Validate file type/size on upload, reject gracefully with clear messages (done in Phase 1/2)
- Handle empty/unreadable PDFs (done in Phase 1/2)
- Handle LLM API failures/timeouts without crashing (done in Phase 1/2)
- Replaced the in-memory document metadata dict with SQLite (`db/database.py`) — fixes the long-standing "documents disappear on restart" limitation
- Added request logging middleware (method, path, status, duration) + DB-init on startup, both in `main.py`
- Added a real pytest suite: chunking logic (`tests/test_chunker.py`), retrieval logic with embeddings mocked for speed (`tests/test_vector_store.py`), and metadata persistence (`tests/test_database.py`) — 12 tests, all passing
- **Done when:** you can't break the app by uploading garbage or spamming requests, and restarting the backend doesn't orphan previously-uploaded documents

## Phase 5 — Polish & UX ✅ DONE
Goal: make it look and feel production-grade.
- Cleaned up UI: upload spinner, friendlier empty-chat state, mobile-responsive layout
- Added a proper landing screen with a "how it works" 3-step explainer
- Added usage limits — 20 questions per uploaded document (`usage_limiter.py`), with live remaining-count shown in the chat header
- README now includes a design decisions table (why Groq, why Chroma, why SQLite, etc.), a project structure map, and a quick-start summary
- **Done when:** a stranger could clone the repo and run it using only the README ✅

## Phase 6 — Deploy & Ship 🔧 PREP DONE, DEPLOY PENDING
Goal: get a live link you can actually share.
- Deploy backend (Render) and frontend (Vercel)
- Set environment variables securely on both platforms (GROQ_API_KEY, CORS_ORIGINS, VITE_API_URL)
- Test the live deployed version end-to-end
- Add the live demo link + screenshots to your GitHub README and resume/portfolio
- Full step-by-step instructions, including free-tier caveats (cold starts, ephemeral storage, possible memory limits), written up in `DEPLOYMENT.md`
- First deploy hit Render's 512MB limit (out-of-memory restarts, surfacing as a CORS error in the browser). Fixed by replacing torch/sentence-transformers with fastembed (ONNX) — same model, much lower RAM
- **Done when:** you can send someone a link and they can use it without you running anything locally — this last step needs you to actually click through Render/Vercel, since I can't do that part for you

## Phase 7 — Stretch Goals (optional, do only if time allows)
- Multi-document support
- Highlight exact source text in an in-browser PDF viewer
- Chat history persistence across sessions
- Support `.docx`/`.txt` uploads
- Simple cost/usage dashboard
