from django.urls import path

from .views import review_create

app_name = "reviews"

urlpatterns = [
    path("create/<int:booking_id>/", review_create, name="create"),
]
