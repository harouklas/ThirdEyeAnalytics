"""URL routes for the public service catalogue."""

from django.urls import path

from . import views

app_name = "catalogue"

urlpatterns = [
    # One list route handles normal browsing, searches and all filters.
    path("services/", views.service_list, name="service_list"),
    # The unique slug gives each service a readable URL instead of a number.
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
]
