from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext

from send_money_agent.prompts import ROOT_AGENT_INSTRUCTION
from send_money_agent.tools import (
    get_delivery_methods_tool,
    lookup_user_by_phone_tool,
    record_transfer_details,
    validate_country_tool,
    validate_delivery_method_tool,
)


def _initialize_state(callback_context: CallbackContext) -> None:
    state = callback_context.state
    state.setdefault("sender_phone", None)
    state.setdefault("sender_name", None)
    state.setdefault("sender_email", None)
    state.setdefault("recipient_name", None)
    state.setdefault("recipient_phone", None)
    state.setdefault("recipient_country", None)
    state.setdefault("amount", None)
    state.setdefault("delivery_method", None)
    state.setdefault("delivery_method_candidate", None)


root_agent = LlmAgent(
    name="send_money_agent",
    model="gemini-2.5-pro",
    description="Collects and confirms money transfer details.",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[
        record_transfer_details,
        lookup_user_by_phone_tool,
        validate_country_tool,
        get_delivery_methods_tool,
        validate_delivery_method_tool,
    ],
    before_agent_callback=_initialize_state,
)
