from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.tutors.models import AvailabilitySlot, Subject, TutorProfile


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_bookings")
    tutor_profile = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="bookings")
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.PROTECT, related_name="booking")
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if self.student.role != "student":
            raise ValidationError("Only students can create bookings.")
        if self.tutor_profile.status != TutorProfile.Status.ACTIVE:
            raise ValidationError("Tutor profile is not active.")
        if self.slot.tutor_profile_id != self.tutor_profile_id:
            raise ValidationError("Selected slot does not belong to this tutor.")
        if self.slot.start_time < timezone.now():
            raise ValidationError("Cannot book past slots.")

    @property
    def can_cancel(self):
        return self.slot.start_time - timezone.now() > timedelta(hours=24)

    def cancel(self):
        if not self.can_cancel:
            raise ValidationError("Booking cannot be cancelled within 24 hours.")
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])


class MockPayment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, default="success")
    paid_at = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Payment<{self.reference}>"
