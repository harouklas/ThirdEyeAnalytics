from django.urls import path

from . import views

app_name = "interactions"

urlpatterns = [
    path("interactions/wishlist/<int:service_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("interactions/rate/<int:service_id>/", views.rate_service, name="rate_service"),
]
