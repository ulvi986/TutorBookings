from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_home, name="home"),
    path("student/", views.student_dashboard, name="student"),
    path("tutor/", views.tutor_dashboard, name="tutor"),
    path("admin/", views.admin_dashboard, name="admin"),
    path("admin/tutor/<int:pk>/approve/", views.approve_tutor, name="approve_tutor"),
    path("admin/tutor/<int:pk>/suspend/", views.suspend_tutor, name="suspend_tutor"),
]
