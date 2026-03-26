# Email Processing Agent — Prototype

An intelligent email triage agent for Tech Managers. Classifies emails by priority, extracts action items, and provides an Outlook-like inbox interface.

## Features

- **Priority Triage**: Classify inbox emails into Act Now / Later / Ignore
- **Action Item Extraction**: Auto-extract to-dos and calendar events from high-priority emails
- **Handled State**: Mark emails as done, with undo support
- **Daily Re-evaluation**: Automatically re-assess "Later" emails as deadlines approach
- **Batch Test Emails**: Upload test emails via Markdown format
- **VIP / Mute Contacts**: Whitelist and blacklist for priority overrides

## Quick Start

```bash
cd email-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your API key

python server.py
# Open http://localhost:8080
```

## Configuration

Edit `.env`:

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL=qwen-plus
```

Supports any OpenAI-compatible API.

## Deploy to Render (Free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect your repo
3. Render auto-detects `render.yaml`. Set environment variables:
   - `OPENAI_API_KEY`
   - `OPENAI_BASE_URL`
   - `OPENAI_MODEL`
4. Click Deploy

## Project Structure

```
email-agent/
├── server.py               # FastAPI backend
├── static/index.html        # Frontend UI
├── src/
│   ├── agent.py             # LLM classification + extraction
│   └── prompts.py           # Prompt templates
├── data/mock_emails.py      # Mock email data
├── docs/                    # Design documentation
├── eval/run_eval.py         # Evaluation script
├── render.yaml              # Render deployment config
└── requirements.txt
```
