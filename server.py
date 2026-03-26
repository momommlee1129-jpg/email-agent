"""FastAPI backend for Email Agent — serves UI and provides LLM API endpoints."""

import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent))

from src.agent import classify_priority, extract_action_items, summarize_thread
from data.mock_emails import MOCK_EMAILS, USER_CONTEXT, LONG_THREAD_EXAMPLE

app = FastAPI(title="Email Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

classifications_cache: dict[str, dict] = {}
actions_cache: dict[str, dict] = {}
_executor = ThreadPoolExecutor(max_workers=5)


def _email_to_json(email: dict) -> dict:
    ts = email["timestamp"]
    time_str = ts.split(" ")[1][:5] if " " in ts else ts
    preview = email["body"][:60].replace("\n", " ") + "..."
    unread = email.get("expected_priority") == "act_now"
    return {
        "id": email["id"],
        "sender": email["from_name"],
        "email": email["from"],
        "subject": email["subject"],
        "preview": preview,
        "body": email["body"],
        "time": time_str,
        "unread": unread,
        "thread_length": email.get("thread_length", 1),
    }


@app.get("/")
async def index():
    return FileResponse("static/index.html")


@app.get("/api/emails")
async def get_emails():
    return {
        "emails": [_email_to_json(e) for e in MOCK_EMAILS],
        "user_context": {
            "user_name": USER_CONTEXT["user_name"],
            "user_role": USER_CONTEXT["user_role"],
        },
    }


@app.get("/api/contacts")
async def get_contacts():
    seen = {}
    for email in MOCK_EMAILS:
        addr = email["from"]
        if addr == USER_CONTEXT["user_email"]:
            continue
        if addr not in seen:
            seen[addr] = {
                "email": addr,
                "name": email["from_name"],
                "email_count": 0,
                "last_subject": email["subject"],
                "last_time": email["timestamp"],
            }
        seen[addr]["email_count"] += 1
    contacts = sorted(seen.values(), key=lambda c: c["email_count"], reverse=True)
    return {"contacts": contacts, "vip_contacts": USER_CONTEXT.get("vip_contacts", [])}


@app.post("/api/classify/{email_id}")
async def classify_email(email_id: str):
    if email_id in classifications_cache:
        return classifications_cache[email_id]

    email = next((e for e in MOCK_EMAILS if e["id"] == email_id), None)
    if not email:
        return JSONResponse(status_code=404, content={"error": "Email not found"})

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, classify_priority, email, USER_CONTEXT)
    classifications_cache[email_id] = result
    return result


@app.post("/api/classify-all")
async def classify_all(limit: int = 0):
    email_list = MOCK_EMAILS if limit <= 0 else MOCK_EMAILS[:limit]

    results = {}
    to_classify = []
    for email in email_list:
        eid = email["id"]
        if eid in classifications_cache:
            results[eid] = classifications_cache[eid]
        else:
            to_classify.append(email)

    if to_classify:
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(_executor, classify_priority, email, USER_CONTEXT)
            for email in to_classify
        ]
        classified = await asyncio.gather(*futures)
        for email, result in zip(to_classify, classified):
            classifications_cache[email["id"]] = result
            results[email["id"]] = result

    return results


@app.post("/api/re-evaluate-later")
async def re_evaluate_later():
    later_emails = [
        e for e in MOCK_EMAILS
        if e["id"] in classifications_cache
        and classifications_cache[e["id"]].get("priority") == "later"
    ]

    if not later_emails:
        return {"changed": [], "total_re_evaluated": 0}

    for e in later_emails:
        classifications_cache.pop(e["id"], None)

    loop = asyncio.get_event_loop()
    futures = [
        loop.run_in_executor(_executor, classify_priority, e, USER_CONTEXT)
        for e in later_emails
    ]
    results = await asyncio.gather(*futures)

    changed = []
    all_results = {}
    for email, result in zip(later_emails, results):
        classifications_cache[email["id"]] = result
        all_results[email["id"]] = result
        if result.get("priority") != "later":
            changed.append({
                "id": email["id"],
                "subject": email["subject"],
                "old_priority": "later",
                "new_priority": result.get("priority"),
            })

    return {
        "changed": changed,
        "total_re_evaluated": len(later_emails),
        "classifications": all_results,
    }


@app.post("/api/extract-actions/{email_id}")
async def extract_actions(email_id: str):
    if email_id in actions_cache:
        return actions_cache[email_id]

    email = next((e for e in MOCK_EMAILS if e["id"] == email_id), None)
    if not email:
        return JSONResponse(status_code=404, content={"error": "Email not found"})

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(_executor, extract_action_items, email, USER_CONTEXT)
    actions_cache[email_id] = result
    return result


class TestEmailInput(BaseModel):
    from_name: str
    from_email: str
    subject: str
    body: str
    to_list: list[str] = []
    cc_list: list[str] = []


custom_email_counter = 0


@app.post("/api/add-email")
async def add_email(payload: TestEmailInput):
    global custom_email_counter
    custom_email_counter += 1
    now = datetime.now()
    eid = f"test_{int(now.timestamp())}_{custom_email_counter}"

    email = {
        "id": eid,
        "from": payload.from_email,
        "from_name": payload.from_name,
        "to": payload.to_list or [USER_CONTEXT["user_email"]],
        "cc": payload.cc_list,
        "subject": payload.subject,
        "body": payload.body,
        "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
        "is_reply": False,
        "thread_length": 1,
    }
    MOCK_EMAILS.insert(0, email)

    cl = classify_priority(email, USER_CONTEXT)
    classifications_cache[eid] = cl

    return {
        "email": _email_to_json(email) | {"unread": True},
        "classification": cl,
    }


@app.post("/api/summarize-thread")
async def summarize():
    return summarize_thread(LONG_THREAD_EXAMPLE, USER_CONTEXT)


app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
