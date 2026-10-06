# DEPLOYMENT.md — Phase 6: Deploy & Ship

Goal: a live link you can put in your portfolio/resume, that works for a
stranger without you running anything locally.

**Order matters here** — deploy the backend first (so you get its URL),
then the frontend (pointing at that URL), then come back and update the
backend once more with the frontend's final URL. Three short stops, not
one long one.

---

## Before you start: two honest things about free hosting

**1. Cold starts.** Render's free tier puts your backend to sleep after
~15 minutes of no traffic. The first request after that takes 30-50
seconds to wake it up (then it's fast again). This is normal — not a bug.
If you're demoing this live to someone, open the link a minute before you
need it to "warm it up."

**2. Storage resets on redeploy.** Free-tier containers don't keep a
persistent disk. That means `backend/chroma_data/` and `backend/data.db`
get wiped every time the service restarts or redeploys — uploaded
documents won't survive that. For a portfolio demo this is an acceptable
tradeoff (visitors upload their own PDF fresh anyway), but it's worth
being able to explain if asked: *"the free tier doesn't persist disk
storage between deploys — the next step up would be Render's paid
persistent disk, or moving to S3 + a managed Postgres."* That sentence
alone is a good signal in an interview.

---

## Step 1 — Get your code on GitHub

Render and Vercel both deploy by connecting to a GitHub repo.

1. Create a new repository on [github.com](https://github.com) (public or
   private, your choice)
2. From your `docchat` folder:
   ```bash
   git init
   git add .
   git commit -m "DocChat: phases 1-5"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/docchat.git
   git push -u origin main
   ```
3. Double check `.env` is **not** in the repo (it's in `.gitignore`, but
   worth a glance at GitHub afterward) — your real API key should never
   be committed.

---

## Step 2 — Deploy the backend to Render

1. Go to [render.com](https://render.com) → sign up (free, GitHub login is easiest)
2. **New +** → **Web Service** → connect your `docchat` repo
3. Configure:
   | Setting | Value |
   |---|---|
   | Name | `docchat-backend` (or anything) |
   | Root Directory | `backend` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | Free |
4. Add environment variables (under **Environment**):
   | Key | Value |
   |---|---|
   | `GROQ_API_KEY` | your real Groq key |
   | `CORS_ORIGINS` | `http://localhost:5173` for now — you'll update this in Step 4 |
   | `PYTHON_VERSION` | `3.11.9` |
5. **Create Web Service**. First deploy takes a few minutes (installing
   torch is the slow part). Watch the logs — you're looking for
   `Uvicorn running on http://0.0.0.0:...` and `Database ready, DocChat
   API starting up.` (that log line is proof Phase 4's logging is working
   in production, not just locally)
6. Once live, copy your backend's URL — it looks like
   `https://docchat-backend-xxxx.onrender.com`
7. Sanity check it: open `https://YOUR-BACKEND-URL/health` in a browser —
   you should see `{"status":"ok"}`

**If the deploy fails with an out-of-memory error:** the free tier's
512MB RAM is genuinely tight for `sentence-transformers` + `torch`. If
this happens, it's worth knowing as a real tradeoff, not a dead end — see
the "If Render's free tier can't fit it" section at the bottom.

---

## Step 3 — Deploy the frontend to Vercel

1. Go to [vercel.com](https://vercel.com) → sign up (free, GitHub login easiest)
2. **Add New** → **Project** → import your `docchat` repo
3. Configure:
   | Setting | Value |
   |---|---|
   | Root Directory | `frontend` |
   | Framework Preset | Vite (should auto-detect) |
   | Build Command | `npm run build` |
   | Output Directory | `dist` |
4. Add an environment variable:
   | Key | Value |
   |---|---|
   | `VITE_API_URL` | your Render backend URL from Step 2 (e.g. `https://docchat-backend-xxxx.onrender.com`) |
5. **Deploy**. Takes about a minute.
6. Copy your frontend's URL — it looks like `https://docchat-yourname.vercel.app`

> Vite bakes environment variables in at **build time**, not runtime. If
> you ever change the backend URL later, you need to update
> `VITE_API_URL` in Vercel's settings *and* trigger a new deploy — just
> saving the env var isn't enough on its own.

---

## Step 4 — Connect them: update CORS on the backend

Right now your backend only allows requests from `localhost:5173` — your
deployed frontend will get CORS errors until you fix this.

1. Back in Render, open your backend service → **Environment**
2. Update `CORS_ORIGINS` to your actual Vercel URL from Step 3, e.g.:
   ```
   CORS_ORIGINS=https://docchat-yourname.vercel.app
   ```
3. Save — Render will automatically redeploy with the new value

---

## Step 5 — Test the live version end to end

Open your Vercel URL in an incognito/private window (so you know it's not
secretly using anything cached locally):
1. Upload a PDF
2. Ask it a question
3. Confirm streaming works and a citation shows up

If the first request hangs for 30-50 seconds, that's the cold start from
the "before you start" note above — not a bug.

---

## Step 6 — Add it to your portfolio

- Put the live Vercel link in your resume/portfolio/LinkedIn
- Take a screenshot of it working (like the one you already have) for your
  README or portfolio site
- In your GitHub repo's README, add the live link near the top so anyone
  browsing the code can try it in one click

---

## If Render's free tier can't fit it

If the backend deploy OOMs, you have a few honest options, roughly in
order of effort:
1. **Try again** — Render's free tier memory can be inconsistent; a retry
   sometimes succeeds
2. **Upgrade the Render instance** one tier (small monthly cost) —
   reasonable if you want this link to be reliably demoable
3. **Swap `sentence-transformers` for an even smaller embedding model** —
   more engineering effort, but keeps everything free
4. **Explain the tradeoff instead of fighting it** — "I hit a real
   resource constraint on free hosting and here's how I'd solve it in
   production" is a legitimate, honest answer in an interview. Not every
   constraint needs to be engineered around to prove you understand it.
