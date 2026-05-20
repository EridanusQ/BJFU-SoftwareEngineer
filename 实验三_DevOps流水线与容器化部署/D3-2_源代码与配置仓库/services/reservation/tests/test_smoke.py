import unittest

from src.main import RESERVATIONS, create_reservation


class ReservationSmokeTest(unittest.TestCase):
    def setUp(self):
        RESERVATIONS.clear()

    def test_create_reservation(self):
        item = create_reservation({
            "memberId": "m_1001",
            "storeId": "s_001",
            "tableId": "t_008",
            "timeSlot": "2026-05-20T18:30:00+08:00/2026-05-20T20:00:00+08:00",
            "partySize": 2,
        })
        self.assertEqual(item["status"], "CONFIRMED")
        self.assertIn(item["id"], RESERVATIONS)

    def test_validation(self):
        with self.assertRaises(ValueError):
            create_reservation({"memberId": "m_1001"})


if __name__ == "__main__":
    unittest.main()
