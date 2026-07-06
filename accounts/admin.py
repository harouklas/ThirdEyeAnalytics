from django.contrib import admin

from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["full_name", "user", "organization", "sport_role", "updated_at"]
    list_filter = ["sport_role", "created_at"]
    search_fields = ["full_name", "user__username", "organization"]
