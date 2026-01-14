import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
AGENTS_DIR = ROOT_DIR / "agents"
sys.path.insert(0, str(AGENTS_DIR))

from send_money_agent.tools import (  # noqa: E402
    get_delivery_methods,
    lookup_user_by_phone,
    normalize_country,
    validate_country,
    validate_delivery_method,
)


def test_validate_country():
    assert validate_country("Mexico")
    assert not validate_country("Atlantis")


def test_normalize_country():
    assert normalize_country("mexico") == "Mexico"
    assert normalize_country("ATLANTIS") is None


def test_lookup_user_by_phone():
    user = lookup_user_by_phone("+15551234567")
    assert user["name"] == "Luis Rueda"
    assert lookup_user_by_phone("+10000000000") is None


def test_delivery_methods():
    methods = get_delivery_methods("Mexico")
    assert "paypal" in methods
    assert validate_delivery_method("Mexico", "paypal")
    assert not validate_delivery_method("Mexico", "venmo")
