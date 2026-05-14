import random
import string
import unittest
from datetime import datetime, timedelta

from nekocafe_quality.domain import (
    ReservationRequest,
    available_slots,
    classify_pet_text,
    create_reservation,
    mask_phone,
    quote_deposit,
    sanitize_note,
)


NOW = datetime(2026, 5, 14, 12, 0)
random.seed(231002703)


class DomainPropertyTest(unittest.TestCase):
    def test_phone_mask_never_exposes_middle_digits(self):
        for _ in range(60):
            suffix = "".join(random.choice(string.digits) for _ in range(8))
            phone = "13" + suffix + "1"
            masked = mask_phone(phone)
            self.assertIn("****", masked)
            self.assertNotIn(phone[3:7], masked)

    def test_deposit_is_non_negative_and_monotonic_for_party_size(self):
        last = 0
        for party in range(1, 9):
            current = quote_deposit(party, 90, vip_level=1)
            self.assertGreaterEqual(current, 0)
            self.assertGreaterEqual(current, last)
            last = current

    def test_available_slots_shrink_when_duration_grows(self):
        short = available_slots(10, 22, 60)
        long = available_slots(10, 22, 180)
        self.assertGreater(len(short), len(long))
        self.assertEqual(short[0], "10:00")

    def test_orange_cat_semantics_are_stable(self):
        cat_phrases = ["橘猫", "我带一只橘猫", "orange cat", "ginger cat"]
        menu_phrases = ["橘子套餐", "orange menu", "咖啡套餐"]
        for text in cat_phrases:
            self.assertEqual(classify_pet_text(text), "cat")
        for text in menu_phrases:
            self.assertEqual(classify_pet_text(text), "menu")

    def test_generated_valid_reservations_have_stable_id_and_safe_note(self):
        for i in range(50):
            req = ReservationRequest(
                customer_id=f"C-{i:04d}",
                phone=f"1380000{i % 10000:04d}",
                party_size=(i % 8) + 1,
                start_at=NOW + timedelta(days=(i % 20) + 1),
                duration_minutes=[30, 60, 90, 120, 180][i % 5],
                table_capacity=8,
                pet_note="橘猫",
                special_note="<b>靠窗</b>",
            )
            first = create_reservation(req, NOW)
            second = create_reservation(req, NOW)
            self.assertEqual(first["reservation_id"], second["reservation_id"])
            self.assertEqual(first["special_note"], sanitize_note("<b>靠窗</b>"))


if __name__ == "__main__":
    unittest.main()
