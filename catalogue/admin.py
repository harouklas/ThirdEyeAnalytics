"""Django admin configuration for catalogue models."""

from django.contrib import admin

from .models import Category, Service, SubCategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name"]


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "slug"]
    list_filter = ["category"]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "category__name"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    # Staff can scan, filter, and search the full service catalogue in Django Admin.
    list_display = [
        "name",
        "category",
        "subcategory",
        "analysis_type",
        "skill_level",
        "price",
        "is_active",
        "is_featured",
    ]
    list_filter = [
        "category",
        "subcategory",
        "analysis_type",
        "skill_level",
        "video_type",
        "delivery_time",
        "output_format",
        "is_active",
        "is_featured",
    ]
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ["name", "short_description", "description"]
