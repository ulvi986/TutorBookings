from django.contrib import admin

from .models import Booking, MockPayment


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "tutor_profile", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("student__email", "tutor_profile__user__email")


@admin.register(MockPayment)
class MockPaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "status", "paid_at", "reference")
    search_fields = ("reference",)
