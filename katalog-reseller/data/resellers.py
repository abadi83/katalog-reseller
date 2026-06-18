"""Reseller data management with JSON file storage."""

import json
import hashlib
import random
import time
from pathlib import Path
from datetime import datetime
from typing import Optional

DATA_DIR = Path(__file__).parent
RESELLERS_FILE = DATA_DIR / "resellers.json"
OTP_FILE = DATA_DIR / "otp_codes.json"


def _load_json(filepath: Path) -> dict:
    """Load JSON file, return empty dict if not found."""
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_json(filepath: Path, data: dict):
    """Save data to JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_all_resellers() -> dict:
    """Get all registered resellers."""
    return _load_json(RESELLERS_FILE)


def get_reseller_by_email(email: str) -> Optional[dict]:
    """Find reseller by email."""
    resellers = _load_json(RESELLERS_FILE)
    for uid, data in resellers.items():
        if data.get("email") == email.lower().strip():
            return {"id": uid, **data}
    return None


def get_reseller_by_phone(phone: str) -> Optional[dict]:
    """Find reseller by phone number."""
    resellers = _load_json(RESELLERS_FILE)
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
    for uid, data in resellers.items():
        stored = data.get("phone", "").replace(" ", "").replace("-", "").replace("+", "")
        if stored == phone_clean:
            return {"id": uid, **data}
    return None


def get_reseller_by_google_id(google_id: str) -> Optional[dict]:
    """Find reseller by Google ID."""
    resellers = _load_json(RESELLERS_FILE)
    for uid, data in resellers.items():
        if data.get("google_id") == google_id:
            return {"id": uid, **data}
    return None


def register_reseller(
    email: str = "",
    phone: str = "",
    password: str = "",
    name: str = "",
    google_id: str = "",
    google_email: str = "",
    google_name: str = "",
    register_method: str = "email",
    upline_code: str = "",
    role: str = "reseller",
) -> dict:
    """Register a new reseller or marketing user. Returns the reseller data dict."""
    resellers = _load_json(RESELLERS_FILE)

    # Generate unique ID
    prefix = "MKT" if role == "marketing" else "RSL"
    uid = f"{prefix}-{int(time.time())}-{random.randint(1000, 9999)}"

    now = datetime.now().isoformat()

    # Find upline by referral code
    upline_id = ""
    if upline_code:
        upline_id = _find_upline_by_code(upline_code, resellers)

    # Generate referral code for marketing users
    referral_code = ""
    if role == "marketing":
        referral_code = _generate_referral_code(name, resellers)

    reseller_data = {
        "nama": name or google_name or ("Marketing" if role == "marketing" else "Reseller Baru"),
        "email": email.lower().strip() if email else google_email.lower().strip(),
        "phone": phone.strip(),
        "role": role,
        "register_method": register_method,
        "created_at": now,
        "is_verified": False,
        "is_active": True,
        "upline_id": upline_id,
        "referral_code": referral_code,
        "commission_rate": 5.0 if role == "marketing" else 0,
    }

    if password:
        reseller_data["password"] = hash_password(password)

    if google_id:
        reseller_data["google_id"] = google_id
        reseller_data["is_verified"] = True

    resellers[uid] = reseller_data
    _save_json(RESELLERS_FILE, resellers)

    # If registered under marketing, update marketing's downline count
    if upline_id and upline_id in resellers:
        resellers[upline_id]["downline_count"] = resellers[upline_id].get("downline_count", 0) + 1
        _save_json(RESELLERS_FILE, resellers)

    return {"id": uid, **reseller_data}


def _generate_referral_code(name: str, existing: dict) -> str:
    """Generate a unique referral code from name."""
    base = name.upper().replace(" ", "")[:6]
    if not base:
        base = "REF"
    while True:
        code = f"{base}{random.randint(100, 999)}"
        # Check uniqueness
        if not any(
            data.get("referral_code") == code for data in existing.values()
        ):
            return code


def _find_upline_by_code(code: str, resellers: dict) -> str:
    """Find a marketing user by referral code. Returns their ID or empty string."""
    for uid, data in resellers.items():
        if data.get("referral_code") == code.upper().strip():
            if data.get("role") == "marketing":
                return uid
    return ""


def get_marketing_by_code(code: str) -> Optional[dict]:
    """Find a marketing user by referral code."""
    resellers = _load_json(RESELLERS_FILE)
    for uid, data in resellers.items():
        if data.get("referral_code") == code.upper().strip():
            if data.get("role") == "marketing":
                return {"id": uid, **data}
    return None


def get_downline_list(marketing_id: str) -> list:
    """Get all resellers under a marketing user."""
    resellers = _load_json(RESELLERS_FILE)
    downline = []
    for uid, data in resellers.items():
        if data.get("upline_id") == marketing_id:
            downline.append({"id": uid, **data})
    return downline


def get_marketing_users() -> list:
    """Get all marketing users."""
    resellers = _load_json(RESELLERS_FILE)
    return [
        {"id": uid, **data}
        for uid, data in resellers.items()
        if data.get("role") == "marketing"
    ]


def verify_reseller(reseller_id: str):
    """Mark a reseller as verified."""
    resellers = _load_json(RESELLERS_FILE)
    if reseller_id in resellers:
        resellers[reseller_id]["is_verified"] = True
        _save_json(RESELLERS_FILE, resellers)
        return True
    return False


# ── OTP System ──


def generate_otp(phone: str) -> str:
    """Generate and store OTP for a phone number. Returns the OTP code."""
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")

    code = str(random.randint(100000, 999999))

    otp_data = _load_json(OTP_FILE)

    # Remove expired OTPs
    now = time.time()
    otp_data = {k: v for k, v in otp_data.items() if v.get("expires", 0) > now}

    otp_data[phone_clean] = {
        "code": code,
        "expires": now + 300,  # 5 minutes
        "attempts": 0,
        "created_at": datetime.now().isoformat(),
    }

    _save_json(OTP_FILE, otp_data)
    return code


def verify_otp(phone: str, code: str) -> bool:
    """Verify an OTP code. Returns True if valid."""
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")

    otp_data = _load_json(OTP_FILE)

    # Clean expired
    now = time.time()
    otp_data = {k: v for k, v in otp_data.items() if v.get("expires", 0) > now}
    _save_json(OTP_FILE, otp_data)

    entry = otp_data.get(phone_clean)
    if not entry:
        return False

    if entry["attempts"] >= 5:
        del otp_data[phone_clean]
        _save_json(OTP_FILE, otp_data)
        return False

    entry["attempts"] += 1
    otp_data[phone_clean] = entry
    _save_json(OTP_FILE, otp_data)

    return entry["code"] == code


def delete_otp(phone: str):
    """Delete OTP entry after successful verification."""
    phone_clean = phone.replace(" ", "").replace("-", "").replace("+", "")
    otp_data = _load_json(OTP_FILE)
    otp_data.pop(phone_clean, None)
    _save_json(OTP_FILE, otp_data)
