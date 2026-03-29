from django.urls import path

from . import views

app_name = "tutors"

urlpatterns = [
    path("", views.tutor_list, name="list"),
    path("<int:pk>/", views.tutor_detail, name="detail"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("availability/", views.availability_manage, name="availability_manage"),
]
