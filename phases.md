# phases.md — Build Phases

## Phase 1 — Bare-bones Q&A (no RAG yet)
Goal: prove the end-to-end flow works before adding complexity.
- Set up FastAPI backend + React frontend skeleton
- Upload a PDF → extract full text with `pdfplumber`
- Send full extracted text + user question directly to Groq API (free tier)
- Display the answer in a simple chat UI (no streaming, no citations yet)
- **Done when:** you can upload a short PDF and get a relevant answer back

## Phase 2 — Real RAG (chunking + retrieval)
Goal: make it scale to long documents and reduce token cost.
- Split extracted text into chunks (~500 tokens, slight overlap), keep page numbers attached
- Generate embeddings for each chunk, store in Chroma
- On each question: embed the question, retrieve top-k similar chunks
- Send only retrieved chunks (not the whole doc) + question to Groq
- **Done when:** a 50+ page PDF works, and retrieval returns the right chunk for a test question

## Phase 3 — Citations + Streaming
Goal: make answers trustworthy and feel responsive.
- Return the page number/chunk source alongside the answer
- Display citation as a small badge/link in the chat UI
- Switch LLM call to streaming; render tokens as they arrive in the UI
- **Done when:** answers appear progressively and each one shows "Source: Page X"

## Phase 4 — Robustness & Error Handling
Goal: make it behave like a real product, not a demo script.
- Validate file type/size on upload, reject gracefully with clear messages
- Handle empty/unreadable PDFs
- Handle LLM API failures/timeouts without crashing
- Add basic logging on backend requests
- Add a few backend tests (chunking logic, retrieval logic)
- **Done when:** you can't break the app by uploading garbage or spamming requests

## Phase 5 — Polish & UX
Goal: make it look and feel production-grade.
- Clean up UI (loading states, empty states, mobile responsiveness)
- Add a proper landing/upload screen, not just a bare chat box
- Add usage limits (e.g., cap questions per session) to control API cost
- Write the README: architecture diagram, setup steps, design decisions, known limitations
- **Done when:** a stranger could clone the repo and run it using only the README

## Phase 6 — Deploy & Ship
Goal: get a live link you can actually share.
- Deploy backend (Render/Railway) and frontend (Vercel/Netlify)
- Set environment variables securely on both platforms
- Test the live deployed version end-to-end
- Add the live demo link + screenshots to your GitHub README and resume/portfolio
- **Done when:** you can send someone a link and they can use it without you running anything locally

## Phase 7 — Stretch Goals (optional, do only if time allows)
- Multi-document support
- Highlight exact source text in an in-browser PDF viewer
- Chat history persistence across sessions
- Support `.docx`/`.txt` uploads
- Simple cost/usage dashboard
