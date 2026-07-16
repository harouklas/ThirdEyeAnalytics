"""Django admin configuration for carts and simulated orders."""

from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    # Show cart items inside the related cart page in Django Admin.
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "updated_at"]
    search_fields = ["user__username"]
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    # Show purchased lines inside the related order page.
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "full_name", "country", "total_price", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = [
        "user__username",
        "full_name",
        "billing_email",
        "organization",
        "vat_number",
    ]
    inlines = [OrderItemInline]
