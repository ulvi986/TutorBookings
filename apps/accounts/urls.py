from django.urls import path

from .views import RegisterView, UserLoginView, UserLogoutView, quick_admin_setup

app_name = "accounts"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("quick-admin/", quick_admin_setup, name="quick_admin"),
]
