from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.accounts.decorators import admin_required, student_required, tutor_required
from apps.bookings.models import Booking
from apps.bookings.views import tutor_earnings_total
from apps.tutors.models import AvailabilitySlot, TutorProfile


@login_required
def dashboard_home(request):
    if request.user.role == "student":
        return redirect("dashboard:student")
    if request.user.role == "tutor":
        return redirect("dashboard:tutor")
    return redirect("dashboard:admin")


@login_required
@student_required
def student_dashboard(request):
    bookings = Booking.objects.filter(student=request.user).select_related("slot", "tutor_profile__user")
    upcoming = bookings.exclude(status=Booking.Status.CANCELLED).filter(slot__start_time__gte=timezone.now())
    return render(request, "dashboard/student_dashboard.html", {"bookings": bookings, "upcoming": upcoming})


@login_required
@tutor_required
def tutor_dashboard(request):
    profile, _ = TutorProfile.objects.get_or_create(user=request.user)
    bookings = Booking.objects.filter(tutor_profile=profile).select_related("student", "slot")
    earnings = tutor_earnings_total(request.user)
    slot_count = AvailabilitySlot.objects.filter(tutor_profile=profile, is_active=True).count()
    return render(
        request,
        "dashboard/tutor_dashboard.html",
        {"profile": profile, "bookings": bookings, "earnings": earnings, "slot_count": slot_count},
    )


@login_required
@admin_required
def admin_dashboard(request):
    pending_tutors = TutorProfile.objects.filter(status=TutorProfile.Status.PENDING)
    stats = {
        "students": request.user.__class__.objects.filter(role="student").count(),
        "tutors": request.user.__class__.objects.filter(role="tutor").count(),
        "bookings": Booking.objects.count(),
        "booking_status": Booking.objects.values("status").annotate(total=Count("id")),
    }
    return render(request, "dashboard/admin_dashboard.html", {"pending_tutors": pending_tutors, "stats": stats})


@login_required
@admin_required
def approve_tutor(request, pk):
    profile = TutorProfile.objects.get(pk=pk)
    profile.status = TutorProfile.Status.ACTIVE
    profile.save(update_fields=["status"])
    return redirect("dashboard:admin")


@login_required
@admin_required
def suspend_tutor(request, pk):
    profile = TutorProfile.objects.get(pk=pk)
    profile.status = TutorProfile.Status.SUSPENDED
    profile.save(update_fields=["status"])
    return redirect("dashboard:admin")
