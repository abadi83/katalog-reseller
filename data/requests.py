"""Reseller Product Request storage."""
import json
import os
from datetime import datetime

REQUESTS_FILE = os.path.join(os.path.dirname(__file__), "requests.json")


def _load_requests() -> list:
    """Load requests from JSON file."""
    if not os.path.exists(REQUESTS_FILE):
        return []
    try:
        with open(REQUESTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def _save_requests(requests: list):
    """Save requests to JSON file."""
    with open(REQUESTS_FILE, "w", encoding="utf-8") as f:
        json.dump(requests, f, ensure_ascii=False, indent=2)


def add_request(reseller_name: str, whatsapp: str, product_name: str,
                brand: str = "", category: str = "", target_price: str = "",
                quantity: str = "", description: str = "", ref_link: str = "",
                reseller_id: str = "") -> dict:
    """Add a new product request."""
    requests = _load_requests()
    req = {
        "id": f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(requests)+1:03d}",
        "reseller_name": reseller_name,
        "reseller_id": reseller_id,
        "whatsapp": whatsapp,
        "product_name": product_name,
        "brand": brand,
        "category": category,
        "target_price": target_price,
        "quantity": quantity,
        "description": description,
        "ref_link": ref_link,
        "status": "pending",  # pending, reviewed, approved, rejected
        "admin_notes": "",
        "created_at": datetime.now().isoformat(),
    }
    requests.insert(0, req)  # newest first
    _save_requests(requests)
    return req


def get_all_requests() -> list:
    """Get all requests (newest first)."""
    return _load_requests()


def get_requests_by_reseller(reseller_id: str) -> list:
    """Get requests by a specific reseller."""
    return [r for r in _load_requests() if r.get("reseller_id") == reseller_id]


def update_request_status(request_id: str, status: str, admin_notes: str = ""):
    """Update request status (admin only)."""
    requests = _load_requests()
    for r in requests:
        if r["id"] == request_id:
            r["status"] = status
            r["admin_notes"] = admin_notes
            break
    _save_requests(requests)


def delete_request(request_id: str):
    """Delete a request."""
    requests = _load_requests()
    requests = [r for r in requests if r["id"] != request_id]
    _save_requests(requests)


def get_pending_count() -> int:
    """Count pending requests."""
    return sum(1 for r in _load_requests() if r["status"] == "pending")
