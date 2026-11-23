from django.urls import path
from .views import (
    home_view,
    spot_detail_view,
    toggle_save_spot_view,
    saved_spots_view,
    add_spot_view,
    toggle_checkin_view,
    add_review_view,
    delete_review_view,
    sql_insights,
)
from apps.login.views import logout_view

app_name = "home"

urlpatterns = [
    path("", home_view, name="home"),
    path("spots/<int:spot_id>/", spot_detail_view, name="spot_detail"),
    path("spots/<int:spot_id>/checkin/", toggle_checkin_view, name="toggle_checkin"),
    path("spots/<int:spot_id>/review/", add_review_view, name="add_review"),
    path("reviews/<int:review_id>/delete/", delete_review_view, name="delete_review"),
    path("save/<int:spot_id>/", toggle_save_spot_view, name="toggle_save"),
    path("saved/", saved_spots_view, name="saved_spots"),
    path("add-spot/", add_spot_view, name="add_spot"),
    path("insights/", sql_insights, name="sql_insights"),
    path("logout/", logout_view, name="logout"),
]
