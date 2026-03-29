from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.tutors.models import TutorProfile

from .forms import LoginForm, RegisterForm
from .models import User


class RegisterView(CreateView):
    template_name = "accounts/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        if user.role == User.Role.TUTOR:
            TutorProfile.objects.get_or_create(user=user)
        login(self.request, user)
        messages.success(self.request, "Registration completed successfully.")
        return response


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm

    def get_success_url(self):
        return reverse_lazy("dashboard:home")


class UserLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


def quick_admin_setup(request):
    if User.objects.filter(role=User.Role.ADMIN).exists():
        return redirect("core:home")
    user = User.objects.create_superuser(
        email="admin@example.com",
        username="admin@example.com",
        full_name="Platform Admin",
        password="admin12345",
    )
    user.role = User.Role.ADMIN
    user.save(update_fields=["role"])
    messages.info(request, "Admin created: admin@example.com / admin12345")
    return redirect("accounts:login")
