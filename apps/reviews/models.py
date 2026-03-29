from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.bookings.models import Booking
from apps.tutors.models import TutorProfile


class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="review")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews_written")
    tutor_profile = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        if not 1 <= self.rating <= 5:
            raise ValidationError("Rating must be between 1 and 5.")
        if self.student.role != "student":
            raise ValidationError("Only students can leave reviews.")
        if self.booking.student_id != self.student_id:
            raise ValidationError("Only booking owner can leave review.")
        if self.booking.status != Booking.Status.COMPLETED:
            raise ValidationError("Review allowed only after session completed.")
        if self.booking.tutor_profile_id != self.tutor_profile_id:
            raise ValidationError("Review tutor mismatch.")

    def __str__(self):
        return f"Review<{self.student.email} -> {self.tutor_profile.user.email}>"
