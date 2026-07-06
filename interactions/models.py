from django.conf import settings
from django.db import models

from catalogue.models import Service


class Rating(models.Model):
    class Score(models.IntegerChoices):
        ONE = 1, "1 star"
        TWO = 2, "2 stars"
        THREE = 3, "3 stars"
        FOUR = 4, "4 stars"
        FIVE = 5, "5 stars"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    score = models.PositiveSmallIntegerField(choices=Score.choices)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "service"],
                name="unique_rating_per_user_service",
            )
        ]

    def __str__(self):
        return f"{self.user.username} rated {self.service.name}: {self.score}"


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="wishlisted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "service"],
                name="unique_wishlist_service_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.service.name}"


class RecentlyViewedService(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="recently_viewed_services",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="recent_views",
    )
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-viewed_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "service"],
                name="unique_recent_service_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user.username} viewed {self.service.name}"


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="search_history",
    )
    query = models.CharField(max_length=150, blank=True)
    analysis_type = models.CharField(max_length=80, blank=True)
    min_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    max_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "search histories"
        ordering = ["-created_at"]

    def __str__(self):
        user_label = self.user.username if self.user else "Public user"
        return f"{user_label} searched for '{self.query}'"
