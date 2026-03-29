from django.urls import path

from . import views

app_name = "bookings"

urlpatterns = [
    path("create/<int:tutor_id>/", views.booking_create, name="create"),
    path("my/", views.my_bookings, name="my"),
    path("tutor/", views.tutor_bookings, name="tutor"),
    path("<int:booking_id>/cancel/", views.cancel_booking, name="cancel"),
    path("<int:booking_id>/mock-pay/", views.mock_pay, name="mock_pay"),
]
