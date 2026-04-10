"""
main.py — FastAPI application for the Dark Pattern Auditor.

Endpoints:
  POST /audit                 — Start an audit, returns { task_id }
  GET  /audit/{task_id}/stream — SSE stream of live progress + findings
  GET  /audit/{task_id}        — Get the full audit result (once complete)
  GET  /health                 — Health check
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid
from typing import AsyncIterator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from classify import classify_steps
from crawler import crawl
from models import AuditRequest, AuditResult, Finding, PatternPrecedents
from precedents import fetch_precedents

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Dark Pattern Auditor API", version="1.0.0")

# Allow the Next.js dev server (and any deployed origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for audit results (sufficient for demo / hackathon use)
_audits: dict[str, AuditResult] = {}
# Per-task event queues for SSE streaming
_event_queues: dict[str, asyncio.Queue] = {}


# ─────────────────────────────── helpers ────────────────────────────────── #

def _get_api_key() -> str:
    key = os.environ.get("PERPLEXITY_API_KEY", "")
    if not key:
        raise HTTPException(status_code=500, detail="PERPLEXITY_API_KEY not configured on server.")
    return key


def _sse_event(event_type: str, data: dict | str) -> str:
    """Format a Server-Sent Events message."""
    if isinstance(data, dict):
        payload = json.dumps(data)
    else:
        payload = json.dumps({"message": data})
    return f"event: {event_type}\ndata: {payload}\n\n"


async def _run_audit(task_id: str, target_url: str, api_key: str) -> None:
    """Background task that runs the full audit pipeline and pushes SSE events."""
    queue = _event_queues[task_id]
    audit = _audits[task_id]
    audit.status = "running"

    async def status(msg: str) -> None:
        logger.info("[%s] %s", task_id, msg)
        await queue.put(_sse_event("status", {"message": msg}))

    try:
        # ── Phase 1: Crawl ──────────────────────────────────────────────── #
        await status(f"Starting crawl of {target_url}…")
        steps = await crawl(target_url, task_id, status_cb=lambda m: asyncio.ensure_future(status(m)))

        if not steps:
            await status("Crawl returned no steps — the site may be inaccessible.")
            audit.status = "complete"
            await queue.put(_sse_event("done", {"task_id": task_id}))
            return

        await status(f"Crawl finished. {len(steps)} step(s) captured. Running AI classification…")

        # ── Phase 2: Classify ───────────────────────────────────────────── #
        findings: list[Finding] = await classify_steps(
            steps,
            target_url,
            api_key,
            status_cb=lambda m: asyncio.ensure_future(status(m)),
        )
        audit.findings = findings

        for finding in findings:
            await queue.put(_sse_event("finding", finding.model_dump()))

        await status(f"Classification complete. {len(findings)} pattern(s) found. Searching precedents…")

        # ── Phase 3: Precedents ─────────────────────────────────────────── #
        if findings:
            precedents: list[PatternPrecedents] = await fetch_precedents(
                findings,
                api_key,
                status_cb=lambda m: asyncio.ensure_future(status(m)),
            )
            audit.precedents = precedents

            for prec in precedents:
                await queue.put(_sse_event("precedents", prec.model_dump()))

        audit.status = "complete"
        await status("Audit complete.")
        await queue.put(_sse_event("done", {"task_id": task_id}))

    except Exception as exc:
        logger.exception("Audit error for task %s: %s", task_id, exc)
        audit.status = "error"
        audit.error = str(exc)
        await queue.put(_sse_event("error", {"message": str(exc)}))
        await queue.put(_sse_event("done", {"task_id": task_id}))
    finally:
        # Signal end of stream with a sentinel
        await queue.put(None)


# ─────────────────────────────── routes ─────────────────────────────────── #

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/audit")
async def start_audit(request: AuditRequest):
    """Start a new audit. Returns { task_id } immediately."""
    api_key = _get_api_key()
    task_id = str(uuid.uuid4())

    audit = AuditResult(
        task_id=task_id,
        target_url=request.url,
        status="pending",
    )
    _audits[task_id] = audit
    _event_queues[task_id] = asyncio.Queue()

    # Fire-and-forget background task
    asyncio.create_task(_run_audit(task_id, request.url, api_key))

    return {"task_id": task_id}


@app.get("/audit/{task_id}/stream")
async def stream_audit(task_id: str):
    """SSE stream — yields events as the audit progresses."""
    if task_id not in _audits:
        raise HTTPException(status_code=404, detail="Audit not found.")

    queue = _event_queues[task_id]

    async def event_generator() -> AsyncIterator[str]:
        # If the audit is already complete, send the full result immediately
        audit = _audits[task_id]
        if audit.status in ("complete", "error"):
            for f in audit.findings:
                yield _sse_event("finding", f.model_dump())
            for p in audit.precedents:
                yield _sse_event("precedents", p.model_dump())
            yield _sse_event("done", {"task_id": task_id})
            return

        # Otherwise stream from the queue
        while True:
            event = await queue.get()
            if event is None:
                break
            yield event

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/audit/{task_id}")
async def get_audit(task_id: str):
    """Get the full audit result."""
    if task_id not in _audits:
        raise HTTPException(status_code=404, detail="Audit not found.")
    return _audits[task_id]


# ─────────────────────────── entry point ────────────────────────────────── #

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("BACKEND_HOST", "0.0.0.0")
    port = int(os.environ.get("BACKEND_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
