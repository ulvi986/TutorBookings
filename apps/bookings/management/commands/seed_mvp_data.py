from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.accounts.models import User
from apps.bookings.models import Booking, MockPayment
from apps.reviews.models import Review
from apps.tutors.models import AvailabilitySlot, Subject, TutorProfile


class Command(BaseCommand):
    help = "Seed MVP sample data"

    def handle(self, *args, **options):
        admin, _ = User.objects.get_or_create(
            email="admin@projectbook.local",
            defaults={"username": "admin@projectbook.local", "full_name": "Admin User", "role": "admin", "is_staff": True, "is_superuser": True},
        )
        admin.set_password("admin12345")
        admin.save()

        subjects = []
        for name, slug in [("Math", "math"), ("Physics", "physics"), ("English", "english")]:
            s, _ = Subject.objects.get_or_create(name=name, slug=slug)
            subjects.append(s)

        tutors = []
        for i in range(1, 4):
            user, _ = User.objects.get_or_create(
                email=f"tutor{i}@mail.com",
                defaults={"username": f"tutor{i}@mail.com", "full_name": f"Tutor {i}", "role": "tutor"},
            )
            user.set_password("pass12345")
            user.save()
            tp, _ = TutorProfile.objects.get_or_create(user=user, defaults={"status": "active", "hourly_rate": Decimal("30.00") + i})
            tp.status = "active"
            tp.save()
            tp.subjects.set(subjects[:2])
            tutors.append(tp)

        students = []
        for i in range(1, 6):
            user, _ = User.objects.get_or_create(
                email=f"student{i}@mail.com",
                defaults={"username": f"student{i}@mail.com", "full_name": f"Student {i}", "role": "student"},
            )
            user.set_password("pass12345")
            user.save()
            students.append(user)

        now = timezone.now() + timedelta(days=2)
        for idx, tutor in enumerate(tutors, 1):
            for h in [10, 14]:
                AvailabilitySlot.objects.get_or_create(
                    tutor_profile=tutor,
                    start_time=now + timedelta(days=idx, hours=h),
                    end_time=now + timedelta(days=idx, hours=h + 1),
                )

        slot = AvailabilitySlot.objects.filter(booking__isnull=True).first()
        if slot:
            booking, _ = Booking.objects.get_or_create(
                student=students[0],
                tutor_profile=slot.tutor_profile,
                slot=slot,
                defaults={"status": "completed"},
            )
            booking.status = "completed"
            booking.save()
            MockPayment.objects.get_or_create(booking=booking, defaults={"amount": slot.tutor_profile.hourly_rate, "reference": "MOCK-SEED-001"})
            Review.objects.get_or_create(
                booking=booking,
                student=students[0],
                tutor_profile=slot.tutor_profile,
                defaults={"rating": 5, "comment": "Great session"},
            )

        self.stdout.write(self.style.SUCCESS("Seed data created."))
