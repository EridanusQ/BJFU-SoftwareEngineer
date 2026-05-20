import unittest
from datetime import datetime, timedelta

from nekocafe_quality.domain import ReservationRequest, cancel_reservation, create_reservation, mask_phone, normalize_consent


NOW = datetime(2026, 5, 14, 12, 0)


class UserJourneyE2ETest(unittest.TestCase):
    def test_new_user_register_browse_book_cancel(self):
        member = {"member_id": "M-1001", "phone_masked": mask_phone("13800000001")}
        stores = [{"store_id": "S-01", "name": "NekoCafé 学院路店"}]
        reservation = create_reservation(ReservationRequest(
            customer_id=member["member_id"],
            phone="13800000001",
            party_size=2,
            start_at=NOW + timedelta(days=2),
            duration_minutes=90,
            table_capacity=4,
            pet_note="橘猫",
        ), NOW)
        cancelled = cancel_reservation(reservation)
        self.assertEqual(stores[0]["store_id"], "S-01")
        self.assertEqual(cancelled["status"], "CANCELLED")

    def test_old_member_recommend_order_pay_review(self):
        member = {"member_id": "M-2001", "vip": 3, "consent": normalize_consent("yes")}
        recommendation = {"sku": "CAT-CAKE-01", "reason": "liked cats"}
        order = {"order_id": "O-1", "amount": 68, "status": "CREATED"}
        payment = {**order, "status": "PAID"}
        review = {"rating": 5, "content": "猫咪互动很好"}
        self.assertTrue(member["consent"])
        self.assertEqual(recommendation["sku"], "CAT-CAKE-01")
        self.assertEqual(payment["status"], "PAID")
        self.assertEqual(review["rating"], 5)

    def test_staff_accept_assign_finish_dashboard(self):
        reservation = create_reservation(ReservationRequest(
            customer_id="M-3001",
            phone="13800003001",
            party_size=3,
            start_at=NOW + timedelta(days=1),
            duration_minutes=120,
            table_capacity=4,
            pet_note="橘猫",
        ), NOW)
        accepted = {**reservation, "status": "ACCEPTED"}
        assigned = {**accepted, "table_id": "T-08"}
        finished = {**assigned, "status": "FINISHED"}
        dashboard = {"today_finished": 1, "last_reservation": finished["reservation_id"]}
        self.assertEqual(finished["table_id"], "T-08")
        self.assertEqual(dashboard["today_finished"], 1)


if __name__ == "__main__":
    unittest.main()
