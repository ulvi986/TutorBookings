from uuid import uuid4

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import student_required, tutor_required
from apps.tutors.models import TutorProfile

from .forms import BookingForm
from .models import Booking, MockPayment


@login_required
@student_required
def booking_create(request, tutor_id):
    tutor = get_object_or_404(TutorProfile, pk=tutor_id, status=TutorProfile.Status.ACTIVE)
    if request.method == "POST":
        form = BookingForm(request.POST, tutor_profile=tutor)
        form.instance.student = request.user
        form.instance.tutor_profile = tutor
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status = Booking.Status.CONFIRMED
            booking.save()
            messages.success(request, "Session booked successfully.")
            return redirect("dashboard:student")
    else:
        form = BookingForm(tutor_profile=tutor)
    return render(request, "bookings/booking_create.html", {"form": form, "tutor": tutor})


@login_required
@student_required
def my_bookings(request):
    bookings = Booking.objects.filter(student=request.user).select_related("tutor_profile__user", "slot")
    return render(request, "bookings/booking_list.html", {"bookings": bookings, "mode": "student"})


@login_required
@tutor_required
def tutor_bookings(request):
    bookings = Booking.objects.filter(tutor_profile__user=request.user).select_related("student", "slot")
    return render(request, "bookings/booking_list.html", {"bookings": bookings, "mode": "tutor"})


@login_required
@student_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, student=request.user)
    try:
        booking.cancel()
        messages.success(request, "Booking cancelled.")
    except ValidationError as exc:
        messages.error(request, str(exc))
    return redirect("bookings:my")


@login_required
@student_required
def mock_pay(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, student=request.user)
    if booking.status not in [Booking.Status.CONFIRMED, Booking.Status.COMPLETED]:
        messages.error(request, "Only confirmed/completed bookings can be paid.")
        return redirect("bookings:my")

    MockPayment.objects.get_or_create(
        booking=booking,
        defaults={"amount": booking.tutor_profile.hourly_rate, "reference": f"MOCK-{uuid4().hex[:10]}"},
    )
    messages.success(request, "Mock payment successful.")
    return redirect("bookings:my")


def tutor_earnings_total(user):
    return (
        MockPayment.objects.filter(booking__tutor_profile__user=user, status="success")
        .aggregate(total=Sum("amount"))
        .get("total")
        or 0
    )
