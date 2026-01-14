import os
import sys
from pathlib import Path

import pytest
from google.adk.runners import InMemoryRunner
from google.genai import types

ROOT_DIR = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT_DIR / "agents"
sys.path.insert(0, str(AGENTS_DIR))

from send_money_agent.agent import root_agent  # noqa: E402

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
def require_api_key():
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY is required for LLM-driven agent tests.")


async def run_message(runner, session, text):
    content = types.Content(role="user", parts=[types.Part(text=text)])
    response_text = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts and event.content.parts[0].text:
            response_text = event.content.parts[0].text
    session = await runner.session_service.get_session(
        app_name=runner.app_name, user_id=session.user_id, session_id=session.id
    )
    return response_text, session


@pytest.mark.asyncio
async def test_agent_flow_smoke():
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user"
    )

    reply, session = await run_message(runner, session, "I want to send money")
    assert reply.strip()


@pytest.mark.asyncio
async def test_agent_flow_multi_field_input():
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user_2"
    )

    reply, session = await run_message(
        runner,
        session,
        "Send 50 to Ana Ruiz in Mexico, phone +5215550000000 via bank_transfer",
    )
    assert reply.strip()
