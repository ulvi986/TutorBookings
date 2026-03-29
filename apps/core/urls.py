from django.urls import path

from .views import HomeView, chatbot_view

app_name = "core"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("chatbot/", chatbot_view, name="chatbot"),
]
