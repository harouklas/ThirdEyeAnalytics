"""Database models for shopping carts and simulated orders."""

from django.conf import settings
from django.db import models

from catalogue.models import Service


class Cart(models.Model):
    # OneToOneField gives each registered user one current shopping cart.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_price(self):
        # The cart total is calculated from its current item totals.
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        # Re-adding a service increases quantity instead of making another row.
        constraints = [
            models.UniqueConstraint(
                fields=["cart", "service"],
                name="unique_service_per_cart",
            )
        ]

    def __str__(self):
        return f"{self.quantity} x {self.service.name}"

    @property
    def line_total(self):
        return self.service.price * self.quantity


class Order(models.Model):
    # Orders are simulated, but statuses make their state clear in the dashboard.
    class Status(models.TextChoices):
        SIMULATED = "simulated", "Simulated"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    full_name = models.CharField(max_length=150)
    billing_email = models.EmailField()
    organization = models.CharField(max_length=150, blank=True)
    billing_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    vat_number = models.CharField(max_length=50, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SIMULATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # The dashboard shows the newest simulated orders first.
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # PROTECT keeps a purchased service available to its historical order item.
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    # Store name and price as a snapshot in case the live service changes later.
    service_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.service_name}"

    @property
    def line_total(self):
        return self.price * self.quantity
