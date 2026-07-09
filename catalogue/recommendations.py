from django.db.models import Q

from interactions.models import RecentlyViewedService, SearchHistory, WishlistItem

from .models import Service


def get_dashboard_recommendations(user, limit=4):
    latest_search = SearchHistory.objects.filter(user=user).first()
    recommendation_filter = Q()

    if latest_search:
        if latest_search.query:
            recommendation_filter |= (
                Q(name__icontains=latest_search.query)
                | Q(short_description__icontains=latest_search.query)
                | Q(description__icontains=latest_search.query)
            )
        if latest_search.analysis_type:
            recommendation_filter |= Q(analysis_type=latest_search.analysis_type)

    recent_category_ids = list(
        RecentlyViewedService.objects.filter(user=user).values_list(
            "service__category_id",
            flat=True,
        )
    )
    wishlist_analysis_types = list(
        WishlistItem.objects.filter(user=user).values_list(
            "service__analysis_type",
            flat=True,
        )
    )

    if recent_category_ids:
        recommendation_filter |= Q(category_id__in=recent_category_ids)

    if wishlist_analysis_types:
        recommendation_filter |= Q(analysis_type__in=wishlist_analysis_types)

    services = Service.objects.filter(is_active=True).select_related(
        "category",
        "subcategory",
    )

    if recommendation_filter:
        services = services.filter(recommendation_filter)
    else:
        services = services.filter(is_featured=True)

    if latest_search and latest_search.min_price is not None:
        services = services.filter(price__gte=latest_search.min_price)

    if latest_search and latest_search.max_price is not None:
        services = services.filter(price__lte=latest_search.max_price)

    already_seen_ids = list(
        RecentlyViewedService.objects.filter(user=user).values_list("service_id", flat=True)
    )
    already_seen_ids += list(
        WishlistItem.objects.filter(user=user).values_list("service_id", flat=True)
    )

    return (
        list(
            services.exclude(id__in=already_seen_ids)
            .distinct()
            .order_by("price", "name")[:limit]
        ),
        latest_search,
    )
