# architecture.md — App Flow & Architecture

## App Flow (MVP)

```
1. User uploads PDF
        │
        ▼
2. Backend extracts text (PyPDF2 / pdfplumber)
        │
        ▼
3. Text is split into chunks (~500 tokens, with overlap)
        │
        ▼
4. Each chunk is converted to an embedding (vector)
        │
        ▼
5. Embeddings stored in a vector store (Chroma, local)
        │
        ▼
6. User types a question in chat UI
        │
        ▼
7. Question is embedded → top-k similar chunks retrieved
        │
        ▼
8. Retrieved chunks + question sent to LLM (Groq API) as context
        │
        ▼
9. LLM generates answer, grounded in the chunks
        │
        ▼
10. Answer streamed back to UI, with page/chunk citation shown
```

## Tech Stack

| Layer            | Choice                              | Why |
|-------------------|--------------------------------------|-----|
| Frontend          | React (Vite)                        | Fast dev, component-based chat UI |
| Styling           | Tailwind CSS                        | Quick, clean, no custom CSS overhead |
| Backend           | Python + FastAPI                    | Simple, async, great for AI/ML glue code |
| PDF parsing       | `pdfplumber`                        | Preserves page numbers for citations |
| Embeddings        | Sentence-Transformers (local, free) | No paid API needed — runs on CPU |
| Vector store      | Chroma (local, file-based)          | Zero-infra setup, good enough for MVP |
| LLM               | Groq API (Llama 3.3 70B)            | Free tier, no credit card, very fast inference |
| Database          | SQLite                              | Store doc metadata + chat history, no server needed |
| Deployment (BE)   | Render / Railway                    | Free tier, easy Python deploys |
| Deployment (FE)   | Vercel / Netlify                    | Free tier, easy React deploys |

> Beginner note: every choice above avoids needing to manage your own servers/infra. Swap to Postgres + Pinecone later only if you outgrow this.

## Folder & File Structure

```
docchat/
├── backend/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── routes/
│   │   ├── upload.py           # POST /upload — handles file ingestion
│   │   └── chat.py             # POST /chat — handles Q&A
│   ├── services/
│   │   ├── pdf_parser.py       # Extract text + page numbers
│   │   ├── chunker.py          # Split text into chunks
│   │   ├── embeddings.py       # Generate + store embeddings
│   │   ├── retriever.py        # Similarity search over chunks
│   │   └── llm.py              # Call Groq API, build prompt
│   ├── models/
│   │   └── schema.py           # Pydantic request/response models
│   ├── db/
│   │   └── database.py         # SQLite setup
│   ├── config.py                # Env vars, constants
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatWindow.jsx
│   │   │   ├── MessageBubble.jsx
│   │   │   ├── UploadBox.jsx
│   │   │   └── CitationBadge.jsx
│   │   ├── hooks/
│   │   │   └── useChat.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
│
├── architecture.md
├── PRD.md
├── rules.md
├── phases.md
└── README.md
```

## Data Flow Summary
- **Storage:** uploaded file → temp storage → parsed → discarded (only chunks + embeddings persist)
- **State:** chat history kept per `document_id` in SQLite
- **Stateless backend:** each `/chat` request includes `document_id`; backend re-fetches relevant chunks each time (no in-memory session reliance)
