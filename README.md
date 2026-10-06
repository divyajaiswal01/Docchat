# DocChat (Phase 1)

Upload a PDF, ask it questions, get answers grounded in the document text.
This is the **Phase 1** build — see `phases.md` for what's next (chunking/RAG,
citations, streaming, deployment).

Planning docs for this project: `PRD.md`, `architecture.md`, `rules.md`, `phases.md`.

## What Phase 1 does
- Upload a PDF → text is extracted
- Ask a question → the full extracted text + question go to an LLM (Groq, free tier)
- Get an answer back in a simple chat UI

No chunking/retrieval yet (that's Phase 2), so this only works well on
shorter documents for now — that's expected.

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

### 4. Try it
Open `http://localhost:5173`, upload a short PDF, and ask it a question.

## Troubleshooting

**"model does not exist or you do not have access to it" (404 from Groq)**
Model availability can vary slightly by account. Check which models your key
can actually use:
```bash
curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer YOUR_GROQ_API_KEY"
```
Then set `MODEL_NAME` in `backend/services/llm.py` to an exact ID from that list.
The default (`llama-3.1-8b-instant`) has the most consistently open free-tier access.

**`TypeError: Client.__init__() got an unexpected keyword argument 'proxies'`**
A newer `httpx` was installed than the `groq` SDK expects. Fix:
```bash
pip install -r requirements.txt --force-reinstall
```

## Known limitations (Phase 1, by design)
- No OCR — scanned/image-only PDFs won't extract text
- No chunking — long documents get truncated (~60k characters) before hitting the LLM
- No persistence — restarting the backend clears uploaded documents (in-memory store)
- No streaming yet — answers appear all at once

These are addressed in later phases, not bugs.
