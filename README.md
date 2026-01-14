# Send Money Agent (ADK)

## Overview
- LLM-driven Send Money Agent built with Google ADK
- Uses ADK's built-in FastAPI server and `/run` endpoint

## Setup
1) Create `.env` (already present) and set:
   - `GOOGLE_API_KEY=your_key`
   - `GOOGLE_GENAI_USE_VERTEXAI=False`

2) Install dependencies (if needed):
```
pip install google-adk fastapi uvicorn pytest pytest-asyncio
```

## Run the API
Start the server:
```
uvicorn main:app --reload
```

Create a session:
```
curl -s -X POST http://127.0.0.1:8000/apps/send_money_agent/users/u1/sessions \
  -H 'Content-Type: application/json' \
  -d '{"state":{"sender_phone":"+15551234567"}}'
```
Copy the `id` from the response and use it as `<SESSION_ID>` below.

Send a message:
```
curl -s -X POST http://127.0.0.1:8000/run \
  -H 'Content-Type: application/json' \
  -d '{
    "app_name":"send_money_agent",
    "user_id":"u1",
    "session_id":"<SESSION_ID>",
    "new_message":{"role":"user","parts":[{"text":"I want to send money"}]}
  }'
```

## Streamlined demo (CLI)
Run a local chat loop that manages the session id:
```
python scripts/send_money_cli.py --sender-phone +15551234567
```

## Testing
Tests require a valid `GOOGLE_API_KEY`.

Run:
```
pytest tests
```
