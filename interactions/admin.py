from django.contrib import admin

from .models import Rating, RecentlyViewedService, SearchHistory, WishlistItem


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["user", "service", "score", "created_at"]
    list_filter = ["score", "created_at"]
    search_fields = ["user__username", "service__name", "comment"]


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ["user", "service", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["user__username", "service__name"]


@admin.register(RecentlyViewedService)
class RecentlyViewedServiceAdmin(admin.ModelAdmin):
    list_display = ["user", "service", "viewed_at"]
    list_filter = ["viewed_at"]
    search_fields = ["user__username", "service__name"]


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "query", "analysis_type", "min_price", "max_price", "created_at"]
    list_filter = ["analysis_type", "created_at"]
    search_fields = ["user__username", "query", "analysis_type"]
