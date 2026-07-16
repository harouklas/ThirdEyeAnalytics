"""Django admin configuration for profile records."""

from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # These options make Profile records easier to review in Django Admin.
    list_display = ["full_name", "user", "role", "organization", "sport_role", "updated_at"]
    list_filter = ["role", "sport_role", "created_at"]
    search_fields = ["full_name", "user__username", "organization"]
