"""URL routes for AJAX wishlist and rating actions."""

from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    # Both POST routes return JSON to the jQuery code on the service page.
    path("interactions/wishlist/<int:service_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("interactions/rate/<int:service_id>/", views.rate_service, name="rate_service"),
]
