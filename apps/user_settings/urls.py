from django.urls import path
from .views import settings_view, toggle_dark_mode_view

app_name = "user_settings"

urlpatterns = [
    path("", settings_view, name="user_settings"),
    path("toggle-dark-mode/", toggle_dark_mode_view, name="toggle_dark_mode"),
]
