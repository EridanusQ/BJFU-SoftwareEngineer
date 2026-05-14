from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from hashlib import sha1


class ReservationError(ValueError):
    def __init__(self, code: str, message: str, details: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}

    def as_dict(self) -> dict:
        return {"code": self.code, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class ReservationRequest:
    customer_id: str
    phone: str
    party_size: int
    start_at: datetime
    duration_minutes: int
    table_capacity: int
    pet_note: str = ""
    special_note: str = ""


def normalize_phone(phone: str) -> str:
    return re.sub(r"\D", "", phone or "")


def mask_phone(phone: str) -> str:
    digits = normalize_phone(phone)
    if len(digits) < 7:
        return "***"
    return f"{digits[:3]}****{digits[-4:]}"


def sanitize_note(note: str, max_len: int = 120) -> str:
    return html.escape((note or "").strip()[:max_len], quote=True)


def normalize_consent(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "同意", "agree"}


def classify_pet_text(text: str) -> str:
    normalized = (text or "").strip().lower()
    if not normalized:
        return "unknown"
    menu_words = ["套餐", "饮品", "咖啡", "甜点", "橘子套餐", "orange menu"]
    cat_words = ["橘猫", "猫咪", "猫", "orange cat", "ginger cat"]
    if any(word in normalized for word in cat_words):
        return "cat"
    if any(word in normalized for word in menu_words):
        return "menu"
    if "dog" in normalized or "狗" in normalized:
        return "dog"
    return "unknown"


def quote_deposit(party_size: int, duration_minutes: int, vip_level: int = 0) -> int:
    if party_size <= 0 or duration_minutes <= 0:
        raise ReservationError("INVALID_DEPOSIT_INPUT", "party size and duration must be positive")
    base = 20 + party_size * 12 + max(duration_minutes - 60, 0) // 30 * 8
    discount = min(max(vip_level, 0), 5) * 2
    return max(base - discount, 0)


def validate_reservation(req: ReservationRequest, now: datetime | None = None) -> dict:
    now = now or datetime.now()
    if not req.customer_id:
        raise ReservationError("CUSTOMER_REQUIRED", "customer id is required")
    phone = normalize_phone(req.phone)
    if len(phone) != 11:
        raise ReservationError("PHONE_INVALID", "phone must contain 11 digits", {"masked": mask_phone(phone)})
    if req.party_size < 1 or req.party_size > 8:
        raise ReservationError("PARTY_SIZE_OUT_OF_RANGE", "party size must be between 1 and 8")
    if req.table_capacity < req.party_size:
        raise ReservationError("TABLE_CAPACITY_NOT_ENOUGH", "table capacity is smaller than party size")
    if req.duration_minutes < 30 or req.duration_minutes > 180:
        raise ReservationError("DURATION_OUT_OF_RANGE", "duration must be between 30 and 180 minutes")
    if req.start_at < now + timedelta(minutes=15):
        raise ReservationError("START_TOO_SOON", "reservation must be at least 15 minutes in the future")
    if req.start_at > now + timedelta(days=30):
        raise ReservationError("START_TOO_LATE", "reservation must be within 30 days")
    if classify_pet_text(req.pet_note) == "menu":
        raise ReservationError("PET_NOTE_NOT_A_PET", "pet note looks like a menu item")
    return {
        "customer_id": req.customer_id,
        "phone_masked": mask_phone(phone),
        "party_size": req.party_size,
        "start_at": req.start_at.isoformat(timespec="minutes"),
        "duration_minutes": req.duration_minutes,
        "pet_type": classify_pet_text(req.pet_note),
        "special_note": sanitize_note(req.special_note),
    }


def create_reservation(req: ReservationRequest, now: datetime | None = None) -> dict:
    valid = validate_reservation(req, now)
    stable_key = f"{valid['customer_id']}|{valid['start_at']}|{valid['party_size']}"
    rid = "RSV-" + sha1(stable_key.encode("utf-8")).hexdigest()[:10].upper()
    deposit = quote_deposit(valid["party_size"], valid["duration_minutes"])
    return {"reservation_id": rid, "status": "CONFIRMED", "deposit": deposit, **valid}


def cancel_reservation(reservation: dict) -> dict:
    status = reservation.get("status")
    if status == "CANCELLED":
        return {**reservation, "status": "CANCELLED", "idempotent": True}
    if status not in {"CONFIRMED", "PENDING"}:
        raise ReservationError("CANCEL_NOT_ALLOWED", "only confirmed or pending reservations can be cancelled")
    return {**reservation, "status": "CANCELLED", "idempotent": False}


def available_slots(open_hour: int, close_hour: int, duration_minutes: int) -> list[str]:
    if open_hour < 0 or close_hour > 24 or close_hour <= open_hour:
        raise ReservationError("BUSINESS_HOURS_INVALID", "business hours are invalid")
    if duration_minutes <= 0:
        raise ReservationError("DURATION_OUT_OF_RANGE", "duration must be positive")
    slots = []
    cursor = open_hour * 60
    end = close_hour * 60
    while cursor + duration_minutes <= end:
        slots.append(f"{cursor // 60:02d}:{cursor % 60:02d}")
        cursor += 30
    return slots
