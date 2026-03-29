from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking
from apps.reviews.models import Review
from apps.tutors.models import AvailabilitySlot, TutorProfile


class BookingRulesTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(email="s@test.com", username="s@test.com", full_name="S", role="student", password="pass12345")
        tutor_user = User.objects.create_user(email="t@test.com", username="t@test.com", full_name="T", role="tutor", password="pass12345")
        self.tutor_profile = TutorProfile.objects.create(user=tutor_user, status="active")
        self.slot = AvailabilitySlot.objects.create(
            tutor_profile=self.tutor_profile,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=1),
        )

    def test_prevent_double_booking(self):
        Booking.objects.create(student=self.student, tutor_profile=self.tutor_profile, slot=self.slot, status="confirmed")
        second_student = User.objects.create_user(email="s2@test.com", username="s2@test.com", full_name="S2", role="student", password="pass12345")
        with self.assertRaises(Exception):
            Booking.objects.create(student=second_student, tutor_profile=self.tutor_profile, slot=self.slot, status="confirmed")

    def test_cancellation_within_24h_not_allowed(self):
        self.slot.start_time = timezone.now() + timedelta(hours=6)
        self.slot.end_time = timezone.now() + timedelta(hours=7)
        self.slot.save()
        booking = Booking.objects.create(student=self.student, tutor_profile=self.tutor_profile, slot=self.slot, status="confirmed")
        with self.assertRaises(ValidationError):
            booking.cancel()

    def test_review_only_after_completed(self):
        booking = Booking.objects.create(student=self.student, tutor_profile=self.tutor_profile, slot=self.slot, status="confirmed")
        review = Review(booking=booking, student=self.student, tutor_profile=self.tutor_profile, rating=5)
        with self.assertRaises(ValidationError):
            review.full_clean()
