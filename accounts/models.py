from django.conf import settings
from django.db import models


class Profile(models.Model):
    class SportRole(models.TextChoices):
        COACH = "coach", "Coach"
        PLAYER = "player", "Player"
        SCOUT = "scout", "Scout"
        ANALYST = "analyst", "Analyst"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=30, blank=True)
    organization = models.CharField(
        max_length=150,
        blank=True,
        help_text="Club, academy, school, or company name.",
    )
    sport_role = models.CharField(
        max_length=30,
        choices=SportRole.choices,
        default=SportRole.COACH,
    )
    favorite_analysis_type = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"
