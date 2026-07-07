from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile
from catalogue.models import Service

from .models import Cart, CartItem, Order, OrderItem


def get_user_cart(user):
    cart, _created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = get_user_cart(request.user)
    items = cart.items.select_related("service", "service__category")

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": cart,
            "items": items,
        },
    )


@login_required
@require_POST
def add_to_cart(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)
    cart = get_user_cart(request.user)
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        service=service,
        defaults={"quantity": 1},
    )

    if not created:
        item.quantity += 1
        item.save(update_fields=["quantity"])

    messages.success(request, f"{service.name} was added to your cart.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart = get_user_cart(request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    service_name = item.service.name
    item.delete()

    messages.success(request, f"{service_name} was removed from your cart.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def checkout(request):
    cart = get_user_cart(request.user)
    items = list(cart.items.select_related("service"))

    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    profile = Profile.objects.filter(user=request.user).first()
    full_name = profile.full_name if profile else request.user.username
    organization = profile.organization if profile else ""
    total_price = sum(item.line_total for item in items)

    order = Order.objects.create(
        user=request.user,
        full_name=full_name,
        organization=organization,
        total_price=total_price,
        status=Order.Status.SIMULATED,
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            service=item.service,
            service_name=item.service.name,
            price=item.service.price,
            quantity=item.quantity,
        )

    cart.items.all().delete()
    messages.success(request, "Checkout simulated successfully.")
    return redirect("cart:checkout_success", order_id=order.id)


@login_required
def checkout_success(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user,
    )

    return render(request, "cart/checkout_success.html", {"order": order})
