from django.urls import path

from . import views

app_name = "catalogue"

urlpatterns = [
    path("services/", views.service_list, name="service_list"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
]
