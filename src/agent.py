"""Core Email Processing Agent — handles priority classification, action item extraction, and thread summary."""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

from .prompts import (
    PRIORITY_CLASSIFICATION_PROMPT,
    ACTION_ITEM_EXTRACTION_PROMPT,
    THREAD_SUMMARY_PROMPT,
)

load_dotenv()


def _get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    )


def _get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _call_llm(prompt: str) -> dict:
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1024,
        )
        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            content = content.rsplit("```", 1)[0]
        return json.loads(content)
    except json.JSONDecodeError:
        return {"error": "Failed to parse LLM response", "raw": content}
    except Exception as e:
        return {"error": str(e)}


def classify_priority(email: dict, user_context: dict) -> dict:
    """Classify an email's priority level using LLM."""
    prompt = PRIORITY_CLASSIFICATION_PROMPT.format(
        user_name=user_context["user_name"],
        user_role=user_context["user_role"],
        vip_contacts=", ".join(user_context["vip_contacts"]),
        calendar_today="\n".join(
            f"  - {evt['time']}: {evt['title']}" for evt in user_context["calendar_today"]
        ),
        active_todos="\n".join(f"  - {t}" for t in user_context["active_todos"]),
        from_name=email["from_name"],
        from_email=email["from"],
        to_list=", ".join(email["to"]),
        cc_list=", ".join(email["cc"]) if email["cc"] else "(none)",
        subject=email["subject"],
        timestamp=email["timestamp"],
        thread_length=email["thread_length"],
        body=email["body"],
    )
    return _call_llm(prompt)


def extract_action_items(email: dict, user_context: dict) -> dict:
    """Extract action items from an email."""
    prompt = ACTION_ITEM_EXTRACTION_PROMPT.format(
        user_name=user_context["user_name"],
        user_role=user_context["user_role"],
        from_name=email["from_name"],
        subject=email["subject"],
        body=email["body"],
    )
    return _call_llm(prompt)


def summarize_thread(thread: dict, user_context: dict) -> dict:
    """Summarize a long email thread."""
    messages_text = "\n\n".join(
        f"[{msg['timestamp']}] {msg['from']}:\n{msg['body']}"
        for msg in thread["messages"]
    )
    prompt = THREAD_SUMMARY_PROMPT.format(
        user_name=user_context["user_name"],
        user_role=user_context["user_role"],
        subject=thread["subject"],
        participants=", ".join(thread["participants"]),
        thread_messages=messages_text,
    )
    return _call_llm(prompt)
