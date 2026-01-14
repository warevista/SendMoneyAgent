import json
from pathlib import Path
from typing import List, Optional

from google.adk.tools import ToolContext

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def _load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_countries() -> List[str]:
    return _load_json(DATA_DIR / "countries.json")


def load_users() -> List[dict]:
    return _load_json(DATA_DIR / "users.json")


def load_delivery_methods() -> dict:
    return _load_json(DATA_DIR / "delivery_methods.json")


def validate_country(country: str) -> bool:
    if not country:
        return False
    countries = load_countries()
    return country.lower() in [c.lower() for c in countries]


def normalize_country(country: str) -> Optional[str]:
    if not country:
        return None
    countries = load_countries()
    for c in countries:
        if c.lower() == country.lower():
            return c
    return None


def lookup_user_by_phone(phone: str) -> Optional[dict]:
    if not phone:
        return None
    for user in load_users():
        if user.get("phone") == phone:
            return user
    return None


def get_delivery_methods(country: str) -> List[str]:
    methods = load_delivery_methods()
    return methods.get(country, [])


def validate_delivery_method(country: str, method: str) -> bool:
    if not country or not method:
        return False
    methods = get_delivery_methods(country)
    return method.lower() in [m.lower() for m in methods]


def normalize_delivery_method(country: str, method: str) -> Optional[str]:
    if not country or not method:
        return None
    methods = get_delivery_methods(country)
    for m in methods:
        if m.lower() == method.lower():
            return m
    return None


def validate_country_tool(country: str, tool_context: ToolContext) -> dict:
    """Checks whether the provided country is supported."""
    normalized = normalize_country(country)
    return {
        "country": normalized,
        "allowed": normalized is not None,
    }


def lookup_user_by_phone_tool(phone: str, tool_context: ToolContext) -> dict:
    """Looks up a registered sender by phone number."""
    user = lookup_user_by_phone(phone)
    if not user:
        return {"status": "not_found"}
    return {"status": "ok", "user": user}


def get_delivery_methods_tool(country: str, tool_context: ToolContext) -> dict:
    """Returns delivery methods available for a supported country."""
    normalized = normalize_country(country)
    if not normalized:
        return {"status": "unsupported_country", "methods": []}
    return {"status": "ok", "methods": get_delivery_methods(normalized)}


def validate_delivery_method_tool(
    country: str, method: str, tool_context: ToolContext
) -> dict:
    """Checks whether a delivery method is valid for the given country."""
    normalized_country = normalize_country(country)
    if not normalized_country:
        return {"status": "unsupported_country", "method": None}
    normalized_method = normalize_delivery_method(normalized_country, method)
    if not normalized_method:
        return {"status": "invalid_method", "method": None}
    return {"status": "ok", "method": normalized_method}


def record_transfer_details(
    tool_context: ToolContext,
    sender_phone: Optional[str] = None,
    sender_name: Optional[str] = None,
    sender_email: Optional[str] = None,
    recipient_name: Optional[str] = None,
    recipient_phone: Optional[str] = None,
    recipient_country: Optional[str] = None,
    amount: Optional[float] = None,
    delivery_method: Optional[str] = None,
) -> dict:
    """Stores any provided transfer fields in the session state."""
    state = tool_context.state
    applied = {}
    ignored = {}

    if sender_phone:
        new_phone = str(sender_phone).strip()
        if state.get("sender_phone") and state.get("sender_phone") != new_phone:
            state["sender_name"] = None
            state["sender_email"] = None
        state["sender_phone"] = new_phone
        applied["sender_phone"] = new_phone
    if sender_name:
        state["sender_name"] = str(sender_name).strip()
        applied["sender_name"] = state["sender_name"]
    if sender_email:
        state["sender_email"] = str(sender_email).strip()
        applied["sender_email"] = state["sender_email"]
    if recipient_name:
        state["recipient_name"] = str(recipient_name).strip()
        applied["recipient_name"] = state["recipient_name"]
    if recipient_phone:
        state["recipient_phone"] = str(recipient_phone).strip()
        applied["recipient_phone"] = state["recipient_phone"]
    if recipient_country:
        normalized = normalize_country(str(recipient_country))
        if normalized:
            if state.get("recipient_country") and state.get("recipient_country") != normalized:
                state["delivery_method"] = None
                state["delivery_method_candidate"] = None
            state["recipient_country"] = normalized
            applied["recipient_country"] = normalized
        else:
            ignored["recipient_country"] = recipient_country
    if amount is not None:
        try:
            state["amount"] = float(amount)
            applied["amount"] = state["amount"]
        except (TypeError, ValueError):
            ignored["amount"] = amount
    if delivery_method:
        method_text = str(delivery_method).strip()
        if state.get("recipient_country"):
            normalized = normalize_delivery_method(
                state["recipient_country"], method_text
            )
            if normalized:
                state["delivery_method"] = normalized
                applied["delivery_method"] = normalized
            else:
                ignored["delivery_method"] = method_text
        else:
            state["delivery_method_candidate"] = method_text
            applied["delivery_method_candidate"] = method_text

    return {"status": "ok", "applied": applied, "ignored": ignored}
