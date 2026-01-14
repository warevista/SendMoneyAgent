from pathlib import Path

from dotenv import load_dotenv


def pytest_sessionstart(session):
    root = Path(__file__).resolve().parents[1]
    load_dotenv(root / ".env")
