"""Views for cart management and simulated checkout."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import Profile
from catalogue.models import Service

from .forms import CheckoutForm
from .models import Cart, CartItem, Order, OrderItem

MAX_CART_QUANTITY = 20


def get_user_cart(user):
    # The cart is created the first time a user needs it.
    cart, _created = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def cart_detail(request):
    cart = get_user_cart(request.user)
    # select_related avoids extra queries while the template loops over the cart.
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
        if item.quantity >= MAX_CART_QUANTITY:
            messages.info(request, f"The maximum quantity for {service.name} is {MAX_CART_QUANTITY}.")
            return redirect("cart:cart_detail")

        # The database keeps one row per service, so another add increases quantity.
        item.quantity += 1
        item.save(update_fields=["quantity"])

    messages.success(request, f"{service.name} was added to your cart.")
    return redirect("cart:cart_detail")


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart = get_user_cart(request.user)
    # Including cart in the lookup stops users removing another user's item by ID.
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    service_name = item.service.name
    item.delete()

    messages.success(request, f"{service_name} was removed from your cart.")
    return redirect("cart:cart_detail")


@login_required
def checkout(request):
    cart = get_user_cart(request.user)
    # Convert the QuerySet to a list because the same items are used several times.
    items = list(cart.items.select_related("service"))

    if not items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_detail")

    # Use account details to pre-fill the billing form on a GET request.
    profile = Profile.objects.filter(user=request.user).first()
    full_name = profile.full_name if profile else request.user.username
    organization = profile.organization if profile else ""
    total_price = sum(item.line_total for item in items)

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Order keeps the customer and billing details for this checkout.
            order = Order.objects.create(
                user=request.user,
                full_name=form.cleaned_data["full_name"],
                billing_email=form.cleaned_data["billing_email"],
                organization=form.cleaned_data["organization"],
                billing_address=form.cleaned_data["billing_address"],
                city=form.cleaned_data["city"],
                postal_code=form.cleaned_data["postal_code"],
                country=form.cleaned_data["country"],
                vat_number=form.cleaned_data["vat_number"],
                total_price=total_price,
                status=Order.Status.SIMULATED,
            )

            # Copy each cart line so later catalogue edits do not change this order.
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    service=item.service,
                    service_name=item.service.name,
                    price=item.service.price,
                    quantity=item.quantity,
                )

            # Clear the cart only after the simulated order has been created.
            cart.items.all().delete()
            messages.success(request, "Checkout simulated successfully.")
            return redirect("cart:checkout_success", order_id=order.id)
    else:
        form = CheckoutForm(
            initial={
                "full_name": full_name,
                "billing_email": request.user.email,
                "organization": organization,
                "country": "Greece",
            }
        )

    return render(
        request,
        "cart/checkout_form.html",
        {
            "form": form,
            "items": items,
            "total_price": total_price,
        },
    )


@login_required
def checkout_success(request, order_id):
    # user=request.user prevents one user opening another user's billing details.
    order = get_object_or_404(
        Order.objects.prefetch_related("items"),
        id=order_id,
        user=request.user,
    )

    return render(request, "cart/checkout_success.html", {"order": order})
