from django.contrib import admin

from .models import AvailabilitySlot, Subject, TutorProfile


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(TutorProfile)
class TutorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "hourly_rate")
    list_filter = ("status", "subjects")
    search_fields = ("user__email", "user__full_name")


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ("tutor_profile", "start_time", "end_time", "is_active")
    list_filter = ("is_active",)
