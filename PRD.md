# PRD.md — Project Requirement Document

## What to Build
**DocChat** — An AI-powered document Q&A web app. A user uploads a document (PDF to start), and can ask natural-language questions about it in a chat interface. Answers are grounded in the actual document content (RAG — Retrieval-Augmented Generation), not hallucinated, and include citations pointing to the source page/section.

**One-line pitch:** "Chat with your PDF — get accurate, cited answers instantly."

## Problem It Solves
Reading long documents (contracts, research papers, reports, manuals) to find specific information is slow. DocChat lets a user ask a question and get a direct, sourced answer instead of manually searching.

## Targeted User
- **Primary:** Students/researchers who need to quickly extract info from papers or textbooks
- **Secondary:** Professionals reviewing contracts, reports, or policy documents
- **Tertiary (stretch):** Small teams wanting a lightweight internal "ask our docs" tool

For portfolio purposes, build for a single generic user first — no need for multi-tenant complexity in v1.

## Core Features (MVP — must have)
1. Upload a PDF document
2. Extract and chunk the document text
3. Ask questions via a chat interface
4. Get an answer grounded in the document content
5. See which page/section the answer came from (citation)
6. Basic error handling (bad file, empty doc, API failure)

## Features (v2 — nice to have, shows depth)
7. Streaming responses (tokens appear as they're generated)
8. Multi-document support (upload several, ask across all of them)
9. Chat history saved per document
10. Support for `.docx` and `.txt` in addition to PDF
11. Download the conversation as a summary

## Features (v3 — stretch, for "wow factor")
12. Highlight the exact source text in the original PDF viewer
13. User accounts + saved document library
14. Usage/cost dashboard (tokens used, cost estimate)

## Out of Scope (explicitly, for v1)
- No user authentication/login (single-user/local use only)
- No multi-tenant data isolation
- No support for scanned/image-only PDFs (OCR) — flag as a known limitation
- No mobile app — web only, responsive design is enough

## Success Criteria
- A stranger can upload a PDF and get a correct, cited answer within ~5 seconds
- The app doesn't crash on bad input (wrong file type, huge file, empty file)
- It's deployed with a live demo link I can put in my portfolio/resume
- README clearly explains the architecture and decisions, demonstrating understanding (not just copy-paste)
