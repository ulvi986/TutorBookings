from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Avg


class Subject(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class TutorProfile(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tutor_profile")
    bio = models.TextField(blank=True)
    education = models.CharField(max_length=255, blank=True)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=20)
    profile_photo = models.ImageField(upload_to="tutor_photos/", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    subjects = models.ManyToManyField(Subject, blank=True)

    def __str__(self):
        return f"TutorProfile<{self.user.email}>"

    @property
    def average_rating(self):
        data = self.reviews.aggregate(avg=Avg("rating"))
        return round(data["avg"] or 0, 2)


class AvailabilitySlot(models.Model):
    tutor_profile = models.ForeignKey(TutorProfile, on_delete=models.CASCADE, related_name="slots")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")
        overlap = AvailabilitySlot.objects.filter(
            tutor_profile=self.tutor_profile,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            is_active=True,
        )
        if self.pk:
            overlap = overlap.exclude(pk=self.pk)
        if overlap.exists():
            raise ValidationError("This slot overlaps an existing slot.")

    def __str__(self):
        return f"{self.tutor_profile.user.full_name}: {self.start_time} - {self.end_time}"
