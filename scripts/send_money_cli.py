import argparse
import json
import sys
from urllib import request


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body)


def _extract_reply(events) -> str:
    for event in reversed(events):
        content = event.get("content") or {}
        parts = content.get("parts") or []
        for part in parts:
            text = part.get("text")
            if text:
                return text
    return json.dumps(events, indent=2)


def create_session(base_url: str, app_name: str, user_id: str, sender_phone: str | None):
    url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions"
    payload = {"state": {}} if sender_phone else {}
    if sender_phone:
        payload["state"]["sender_phone"] = sender_phone
    session = _post_json(url, payload)
    return session["id"]


def run_message(base_url: str, app_name: str, user_id: str, session_id: str, message: str) -> str:
    url = f"{base_url}/run"
    payload = {
        "app_name": app_name,
        "user_id": user_id,
        "session_id": session_id,
        "new_message": {"role": "user", "parts": [{"text": message}]},
    }
    events = _post_json(url, payload)
    return _extract_reply(events)


def main() -> int:
    parser = argparse.ArgumentParser(description="Send Money Agent CLI")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--app", default="send_money_agent")
    parser.add_argument("--user", default="u1")
    parser.add_argument("--sender-phone")
    args = parser.parse_args()

    session_id = create_session(args.base_url, args.app, args.user, args.sender_phone)
    print(f"Session: {session_id}")
    print("Type messages. Use /quit to exit.")

    while True:
        try:
            message = input("> ").strip()
        except EOFError:
            print()
            break
        if not message:
            continue
        if message.lower() in {"/quit", "/exit", "quit", "exit"}:
            break
        reply = run_message(args.base_url, args.app, args.user, session_id, message)
        print(reply)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
