import unittest
from datetime import datetime, timedelta

from nekocafe_quality.domain import ReservationError, ReservationRequest, cancel_reservation, create_reservation, validate_reservation


NOW = datetime(2026, 5, 14, 12, 0)


class InMemoryReservationRepository:
    def __init__(self):
        self.rows = {}

    def save(self, reservation):
        self.rows[reservation["reservation_id"]] = reservation
        return reservation

    def get(self, reservation_id):
        return self.rows[reservation_id]


def req(index=1, **overrides):
    data = {
        "customer_id": f"C-{index:04d}",
        "phone": f"1380000{index:04d}",
        "party_size": 2,
        "start_at": NOW + timedelta(days=1, hours=index % 5),
        "duration_minutes": 90,
        "table_capacity": 4,
        "pet_note": "橘猫",
        "special_note": "靠窗",
    }
    data.update(overrides)
    return ReservationRequest(**data)


class ReservationIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryReservationRepository()

    def test_create_and_read_reservation(self):
        saved = self.repo.save(create_reservation(req(1), NOW))
        self.assertEqual(self.repo.get(saved["reservation_id"])["status"], "CONFIRMED")

    def test_cancel_flow_updates_state(self):
        saved = self.repo.save(create_reservation(req(2), NOW))
        cancelled = cancel_reservation(saved)
        self.repo.save(cancelled)
        self.assertEqual(self.repo.get(saved["reservation_id"])["status"], "CANCELLED")

    def test_duplicate_request_generates_same_id(self):
        self.assertEqual(create_reservation(req(3), NOW)["reservation_id"], create_reservation(req(3), NOW)["reservation_id"])

    def test_capacity_error_does_not_persist(self):
        with self.assertRaises(ReservationError):
            self.repo.save(create_reservation(req(4, party_size=5, table_capacity=4), NOW))
        self.assertEqual(len(self.repo.rows), 0)

    def test_phone_error_does_not_persist(self):
        with self.assertRaises(ReservationError):
            create_reservation(req(5, phone="123"), NOW)
        self.assertEqual(len(self.repo.rows), 0)

    def test_future_boundary_accepts_day_30(self):
        result = validate_reservation(req(6, start_at=NOW + timedelta(days=30)), NOW)
        self.assertEqual(result["party_size"], 2)

    def test_future_boundary_rejects_day_31(self):
        with self.assertRaises(ReservationError):
            validate_reservation(req(7, start_at=NOW + timedelta(days=31)), NOW)

    def test_menu_note_rejected(self):
        with self.assertRaises(ReservationError):
            create_reservation(req(8, pet_note="橘子套餐"), NOW)

    def test_special_note_is_escaped(self):
        saved = create_reservation(req(9, special_note="<script>x</script>"), NOW)
        self.assertIn("&lt;script&gt;", saved["special_note"])

    def test_many_reservations_have_unique_ids(self):
        ids = {create_reservation(req(i), NOW)["reservation_id"] for i in range(10, 20)}
        self.assertEqual(len(ids), 10)

    def test_cancelled_reservation_is_idempotent(self):
        cancelled = cancel_reservation(create_reservation(req(20), NOW))
        again = cancel_reservation(cancelled)
        self.assertTrue(again["idempotent"])

    def test_invalid_cancel_state_raises(self):
        with self.assertRaises(ReservationError):
            cancel_reservation({"reservation_id": "RSV-X", "status": "PAID"})


if __name__ == "__main__":
    unittest.main()
