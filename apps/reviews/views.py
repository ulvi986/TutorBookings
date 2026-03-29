from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import student_required
from apps.bookings.models import Booking

from .forms import ReviewForm


@login_required
@student_required
def review_create(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, student=request.user)
    if hasattr(booking, "review"):
        messages.info(request, "Review already submitted for this booking.")
        return redirect("dashboard:student")

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.student = request.user
            review.tutor_profile = booking.tutor_profile
            review.full_clean()
            review.save()
            messages.success(request, "Review submitted.")
            return redirect("dashboard:student")
    else:
        form = ReviewForm()

    return render(request, "reviews/review_form.html", {"form": form, "booking": booking})
