"""URL routes for cart and checkout pages."""

from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    # cart_detail loads the cart that belongs to request.user.
    path("cart/", views.cart_detail, name="cart_detail"),
    # Add and remove accept POST because they change saved data.
    path("cart/add/<int:service_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),
    # Checkout first collects details and then redirects to the saved order.
    path("cart/checkout/", views.checkout, name="checkout"),
    path("cart/checkout/<int:order_id>/", views.checkout_success, name="checkout_success"),
]
