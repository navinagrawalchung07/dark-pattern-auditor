# Dark Pattern Auditor

A full-stack legal audit tool that navigates websites with real browser automation, classifies dark patterns against live FTC and EU statutes using AI, and surfaces real enforcement precedents — all in a professional report UI.

## What It Does

1. **Crawl** — Playwright navigates signup, cancellation, and cookie-consent flows, capturing screenshots and page text at each step.
2. **Classify** — Perplexity `sonar-reasoning-pro` fetches live statute text from `ftc.gov` and `ec.europa.eu` at classification time and identifies dark patterns with legal citations.
3. **Precedents** — A second Perplexity call finds real FTC/EU enforcement cases for each pattern found.
4. **Report** — A Next.js frontend streams live progress, then renders a structured legal audit report with screenshot thumbnails, severity badges, statute excerpts, and enforcement precedents.

## Dark Patterns Detected

| Pattern | Severity Range |
|---|---|
| `roach_motel` | medium → high |
| `confirmshaming` | low → medium |
| `hidden_costs` | medium → high |
| `trick_questions` | low → high |
| `disguised_ads` | medium → high |
| `forced_continuity` | high |
| `misdirection` | low → high |

---

## Tech Stack

- **Backend**: Python FastAPI (async) with SSE streaming
- **Browser automation**: Playwright (Chromium, headless)
- **AI**: Perplexity `sonar-reasoning-pro` with live `fetch_url` tool calls
- **Frontend**: Next.js 14 + Tailwind CSS

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- A [Perplexity API key](https://www.perplexity.ai/settings/api)

---

### Backend

```bash
cd backend

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Configure environment
cp ../.env.example .env
# Edit .env and add your PERPLEXITY_API_KEY

# Start the backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be running at `http://localhost:8000`.

---

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp ../.env.example .env.local
# NEXT_PUBLIC_API_URL should point to your backend (default: http://localhost:8000)

# Start the frontend dev server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

---

## Usage

1. Open the app at `http://localhost:3000`
2. Paste any website URL into the input field
3. Click **Run Audit**
4. Watch the live crawler status stream as Playwright navigates the site
5. Review the structured report — each finding card shows:
   - Pattern type badge (color-coded by severity)
   - Screenshot thumbnail from the crawl
   - Quoted UI text from the page
   - Statute name + excerpt (fetched live from FTC/EU sites)
   - Enforcement precedents with case names, outcomes, and source links

---

## API Reference

### `POST /audit`

Start an audit. Returns a `task_id`.

```json
{ "url": "https://example.com" }
```

### `GET /audit/{task_id}/stream`

SSE stream of audit progress events. Event types:
- `status` — crawler progress message
- `finding` — a new dark pattern finding (JSON)
- `precedents` — enforcement cases for a pattern (JSON)
- `done` — audit complete
- `error` — audit failed

### `GET /audit/{task_id}`

Get the full audit result once complete.

---

## Project Structure

```
dark-pattern-auditor/
├── backend/
│   ├── main.py           # FastAPI app + SSE streaming
│   ├── crawler.py        # Playwright browser automation
│   ├── classify.py       # Perplexity dark pattern classification
│   ├── precedents.py     # Perplexity enforcement case search
│   ├── models.py         # Pydantic data models
│   ├── requirements.txt
│   └── screenshots/      # Auto-created, gitignored
├── frontend/
│   ├── app/
│   │   ├── page.tsx      # Main audit UI
│   │   └── layout.tsx
│   ├── components/
│   │   ├── AuditForm.tsx
│   │   ├── StatusStream.tsx
│   │   ├── FindingCard.tsx
│   │   └── PrecedentCard.tsx
│   ├── package.json
│   └── tailwind.config.ts
├── .env.example
├── .gitignore
└── README.md
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `PERPLEXITY_API_KEY` | Yes | Your Perplexity API key |
| `BACKEND_HOST` | No | Backend bind host (default `0.0.0.0`) |
| `BACKEND_PORT` | No | Backend port (default `8000`) |
| `NEXT_PUBLIC_API_URL` | No | Backend URL for frontend (default `http://localhost:8000`) |

---

## Legal Notice

This tool is designed for research, compliance, and regulatory audit purposes. Classifications are AI-generated and reference publicly available statute text. They do not constitute legal advice. Always consult a qualified attorney before taking legal action.
