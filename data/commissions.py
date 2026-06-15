"""Commission tracking for Marketing ↔ Reseller system."""

import json
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).parent
COMMISSIONS_FILE = DATA_DIR / "commissions.json"


def _load() -> list:
    if COMMISSIONS_FILE.exists():
        with open(COMMISSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(data: list):
    with open(COMMISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_commission(
    marketing_id: str,
    marketing_name: str,
    reseller_id: str,
    reseller_name: str,
    order_amount: int,
    commission_rate: float,
) -> dict:
    """Record a commission when a reseller makes a purchase."""
    commissions = _load()

    commission_amount = int(order_amount * commission_rate / 100)

    entry = {
        "id": f"COM-{int(time.time())}-{random.randint(100, 999)}",
        "marketing_id": marketing_id,
        "marketing_name": marketing_name,
        "reseller_id": reseller_id,
        "reseller_name": reseller_name,
        "order_amount": order_amount,
        "commission_rate": commission_rate,
        "commission_amount": commission_amount,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    commissions.append(entry)
    _save(commissions)

    return entry


def get_commissions_for_marketing(marketing_id: str) -> list:
    """Get all commissions for a marketing user, newest first."""
    commissions = _load()
    result = [
        c for c in commissions if c["marketing_id"] == marketing_id
    ]
    return sorted(result, key=lambda x: x["created_at"], reverse=True)


def get_total_commission(marketing_id: str) -> int:
    """Get total commission earned by a marketing user."""
    commissions = _load()
    return sum(
        c["commission_amount"]
        for c in commissions
        if c["marketing_id"] == marketing_id
    )


def get_pending_commission(marketing_id: str) -> int:
    """Get pending (unpaid) commission total."""
    commissions = _load()
    return sum(
        c["commission_amount"]
        for c in commissions
        if c["marketing_id"] == marketing_id and c.get("status") == "pending"
    )


def mark_as_paid(commission_id: str) -> bool:
    """Mark a commission as paid."""
    commissions = _load()
    for c in commissions:
        if c["id"] == commission_id:
            c["status"] = "paid"
            _save(commissions)
            return True
    return False


def get_all_commissions() -> list:
    """Get all commissions, newest first."""
    return sorted(_load(), key=lambda x: x["created_at"], reverse=True)
