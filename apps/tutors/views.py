from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import tutor_required

from .forms import AvailabilitySlotForm, TutorProfileForm
from .models import AvailabilitySlot, TutorProfile


def tutor_list(request):
    tutors = TutorProfile.objects.filter(status=TutorProfile.Status.ACTIVE).annotate(avg_rating=Avg("reviews__rating"))
    q = request.GET.get("q", "").strip()
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    min_rating = request.GET.get("min_rating")
    sort = request.GET.get("sort")

    if q:
        tutors = tutors.filter(Q(user__full_name__icontains=q) | Q(subjects__name__icontains=q)).distinct()
    if price_min:
        tutors = tutors.filter(hourly_rate__gte=price_min)
    if price_max:
        tutors = tutors.filter(hourly_rate__lte=price_max)
    if min_rating:
        tutors = tutors.filter(avg_rating__gte=min_rating)
    if sort == "rating_desc":
        tutors = tutors.order_by("-avg_rating")
    elif sort == "price_asc":
        tutors = tutors.order_by("hourly_rate")

    return render(request, "tutors/tutor_list.html", {"tutors": tutors})


def tutor_detail(request, pk):
    tutor = get_object_or_404(TutorProfile, pk=pk, status=TutorProfile.Status.ACTIVE)
    reviews = tutor.reviews.select_related("student").order_by("-created_at")
    slots = tutor.slots.filter(is_active=True)
    return render(request, "tutors/tutor_detail.html", {"tutor": tutor, "reviews": reviews, "slots": slots})


@login_required
@tutor_required
def profile_edit(request):
    profile, _ = TutorProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = TutorProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            obj = form.save(commit=False)
            if obj.status == TutorProfile.Status.SUSPENDED:
                messages.error(request, "Profile is suspended by admin.")
            else:
                if obj.status != TutorProfile.Status.ACTIVE:
                    obj.status = TutorProfile.Status.PENDING
                obj.save()
                form.save_m2m()
                messages.success(request, "Tutor profile updated.")
                return redirect("dashboard:home")
    else:
        form = TutorProfileForm(instance=profile)
    return render(request, "tutors/tutor_profile_form.html", {"form": form, "profile": profile})


@login_required
@tutor_required
def availability_manage(request):
    profile, _ = TutorProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = AvailabilitySlotForm(request.POST)
        form.instance.tutor_profile = profile
        if form.is_valid():
            form.save()
            messages.success(request, "Availability slot added.")
            return redirect("tutors:availability_manage")
    else:
        form = AvailabilitySlotForm()

    slots = AvailabilitySlot.objects.filter(tutor_profile=profile)
    return render(request, "tutors/availability_manage.html", {"form": form, "slots": slots})
