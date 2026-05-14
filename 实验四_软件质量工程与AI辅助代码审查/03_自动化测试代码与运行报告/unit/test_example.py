import unittest
from datetime import datetime, timedelta

from nekocafe_quality.domain import (
    ReservationError,
    ReservationRequest,
    available_slots,
    cancel_reservation,
    classify_pet_text,
    create_reservation,
    mask_phone,
    normalize_consent,
    quote_deposit,
    sanitize_note,
    validate_reservation,
)


NOW = datetime(2026, 5, 14, 12, 0)


def make_request(**overrides):
    data = {
        "customer_id": "C-1001",
        "phone": "13800000001",
        "party_size": 2,
        "start_at": NOW + timedelta(days=1),
        "duration_minutes": 90,
        "table_capacity": 4,
        "pet_note": "橘猫",
        "special_note": "靠窗",
    }
    data.update(overrides)
    return ReservationRequest(**data)


class ReservationUnitTest(unittest.TestCase):
    def test_create_reservation_success(self):
        result = create_reservation(make_request(), NOW)
        self.assertEqual(result["status"], "CONFIRMED")
        self.assertTrue(result["reservation_id"].startswith("RSV-"))
        self.assertEqual(result["pet_type"], "cat")

    def test_zero_party_size_rejected(self):
        with self.assertRaises(ReservationError) as ctx:
            validate_reservation(make_request(party_size=0), NOW)
        self.assertEqual(ctx.exception.code, "PARTY_SIZE_OUT_OF_RANGE")

    def test_table_capacity_must_cover_party(self):
        with self.assertRaises(ReservationError) as ctx:
            validate_reservation(make_request(party_size=5, table_capacity=4), NOW)
        self.assertEqual(ctx.exception.code, "TABLE_CAPACITY_NOT_ENOUGH")

    def test_duration_boundary(self):
        self.assertEqual(validate_reservation(make_request(duration_minutes=30), NOW)["duration_minutes"], 30)
        with self.assertRaises(ReservationError):
            validate_reservation(make_request(duration_minutes=181), NOW)

    def test_start_time_boundary(self):
        with self.assertRaises(ReservationError):
            validate_reservation(make_request(start_at=NOW + timedelta(minutes=10)), NOW)
        with self.assertRaises(ReservationError):
            validate_reservation(make_request(start_at=NOW + timedelta(days=31)), NOW)

    def test_orange_cat_not_orange_menu(self):
        self.assertEqual(classify_pet_text("橘猫"), "cat")
        self.assertEqual(classify_pet_text("橘子套餐"), "menu")

    def test_cancel_is_idempotent(self):
        res = create_reservation(make_request(), NOW)
        cancelled = cancel_reservation(res)
        again = cancel_reservation(cancelled)
        self.assertTrue(again["idempotent"])

    def test_privacy_helpers(self):
        self.assertEqual(mask_phone("138-0000-0001"), "138****0001")
        self.assertEqual(normalize_consent("同意"), True)
        self.assertIn("&lt;script&gt;", sanitize_note("<script>alert(1)</script>"))

    def test_error_payload_as_dict(self):
        err = ReservationError("X_TEST", "message", {"field": "party_size"})
        self.assertEqual(err.as_dict()["code"], "X_TEST")
        self.assertEqual(err.as_dict()["details"]["field"], "party_size")

    def test_unknown_and_dog_classification(self):
        self.assertEqual(classify_pet_text(""), "unknown")
        self.assertEqual(classify_pet_text("small dog"), "dog")
        self.assertEqual(classify_pet_text("蓝莓蛋糕"), "unknown")

    def test_invalid_deposit_input_rejected(self):
        with self.assertRaises(ReservationError) as ctx:
            quote_deposit(0, 90)
        self.assertEqual(ctx.exception.code, "INVALID_DEPOSIT_INPUT")

    def test_available_slots_standard_and_invalid_hours(self):
        self.assertEqual(available_slots(10, 12, 60), ["10:00", "10:30", "11:00"])
        with self.assertRaises(ReservationError):
            available_slots(22, 10, 60)

    def test_short_phone_mask_and_false_consent(self):
        self.assertEqual(mask_phone("123"), "***")
        self.assertFalse(normalize_consent(None))
        self.assertFalse(normalize_consent("no"))

    def test_customer_required(self):
        with self.assertRaises(ReservationError) as ctx:
            validate_reservation(make_request(customer_id=""), NOW)
        self.assertEqual(ctx.exception.code, "CUSTOMER_REQUIRED")


if __name__ == "__main__":
    unittest.main()
