"""Database model for extra user profile information."""

from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


phone_number_validator = RegexValidator(
    regex=r"^[0-9]{6,15}$",
    message="Enter 6 to 15 numbers without spaces or symbols.",
)


class Profile(models.Model):
    # These are the three access roles that can belong to a registered account.
    class UserRole(models.TextChoices):
        HEAD_ADMINISTRATOR = "head_administrator", "Head Administrator"
        ADMINISTRATOR = "administrator", "Administrator"
        USER = "user", "User"

    # This role describes the user's football background, not their permissions.
    class SportRole(models.TextChoices):
        COACH = "coach", "Coach"
        PLAYER = "player", "Player"
        SCOUT = "scout", "Scout"
        ANALYST = "analyst", "Analyst"
        OTHER = "other", "Other"

    class PhoneCountry(models.TextChoices):
        GREECE = "+30", "Greece (+30)"
        CYPRUS = "+357", "Cyprus (+357)"
        UNITED_KINGDOM = "+44", "United Kingdom (+44)"
        UNITED_STATES = "+1", "United States / Canada (+1)"
        GERMANY = "+49", "Germany (+49)"
        FRANCE = "+33", "France (+33)"
        ITALY = "+39", "Italy (+39)"
        SPAIN = "+34", "Spain (+34)"

    # Each Django User has one ThirdEye profile with the extra business information.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.USER,
    )
    full_name = models.CharField(max_length=150)
    phone_country_code = models.CharField(
        max_length=6,
        choices=PhoneCountry.choices,
        default=PhoneCountry.GREECE,
    )
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        validators=[phone_number_validator],
    )
    organization = models.CharField(
        max_length=25,
        blank=True,
        help_text="Club, academy, school, or company name.",
    )
    sport_role = models.CharField(
        max_length=30,
        choices=SportRole.choices,
        default=SportRole.COACH,
    )
    favorite_analysis_type = models.CharField(max_length=80, blank=True)
    bio = models.TextField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # User lists show profiles alphabetically by username unless another order is requested.
        ordering = ["user__username"]

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"
