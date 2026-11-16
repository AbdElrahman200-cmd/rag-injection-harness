import json
from pathlib import Path

_DATA = json.loads(
    (Path(__file__).parent / "data" / "customers.json").read_text(encoding="utf-8")
)

def get_customer(customer_id: str) -> dict:
    return _DATA.get(customer_id.upper(), {})