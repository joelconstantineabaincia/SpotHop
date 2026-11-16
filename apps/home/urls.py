from django.urls import path
from .views import (
    home_view,
    toggle_save_spot_view,
    saved_spots_view,
    add_spot_view,
)
from apps.login.views import logout_view

app_name = "home"

urlpatterns = [
    path("", home_view, name="home"),
    path("save/<int:spot_id>/", toggle_save_spot_view, name="toggle_save"),
    path("saved/", saved_spots_view, name="saved_spots"),
    path("add-spot/", add_spot_view, name="add_spot"),
    path("logout/", logout_view, name="logout"),
]
