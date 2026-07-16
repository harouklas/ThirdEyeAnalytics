"""Views for searching, filtering, and viewing catalogue services."""

from decimal import Decimal, InvalidOperation

from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render

from interactions.models import Rating, RecentlyViewedService, SearchHistory, WishlistItem

from .models import Category, Service, SubCategory

MAX_SERVICE_PRICE = Decimal("999999.99")


def valid_choice(value, choices):
    """Return only values that exist in one of the model's choice lists."""
    allowed_values = {choice_value for choice_value, _label in choices}
    return value if value in allowed_values else ""


def valid_price(value):
    """Convert a short, positive price string or return no filter value."""
    value = value.strip()[:20]
    if not value:
        return "", None

    try:
        decimal_value = Decimal(value)
    except InvalidOperation:
        return "", None

    if not decimal_value.is_finite() or not 0 <= decimal_value <= MAX_SERVICE_PRICE:
        return "", None

    return value, decimal_value


def service_list(request):
    # select_related avoids another database query for each service card.
    services = (
        Service.objects.filter(is_active=True)
        .select_related("category", "subcategory")
        .order_by("name")
    )

    # GET values come from the search and filter controls in the catalogue page.
    query = request.GET.get("q", "").strip()[:150]
    category_slug = request.GET.get("category", "")[:120]
    subcategory_slug = request.GET.get("subcategory", "")[:120]
    analysis_type = valid_choice(
        request.GET.get("analysis_type", "")[:80],
        Service.AnalysisType.choices,
    )
    skill_level = valid_choice(
        request.GET.get("skill_level", "")[:30],
        Service.SkillLevel.choices,
    )
    video_type = valid_choice(
        request.GET.get("video_type", "")[:30],
        Service.VideoType.choices,
    )
    delivery_time = valid_choice(
        request.GET.get("delivery_time", "")[:30],
        Service.DeliveryTime.choices,
    )
    output_format = valid_choice(
        request.GET.get("output_format", "")[:30],
        Service.OutputFormat.choices,
    )
    min_price, min_price_value = valid_price(request.GET.get("min_price", ""))
    max_price, max_price_value = valid_price(request.GET.get("max_price", ""))

    if query:
        # A text search can match the name or either description field.
        services = services.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
        )

    # Each value that was actually selected narrows the same result list.
    if category_slug:
        services = services.filter(category__slug=category_slug)

    if subcategory_slug:
        services = services.filter(subcategory__slug=subcategory_slug)

    if analysis_type:
        services = services.filter(analysis_type=analysis_type)

    if skill_level:
        services = services.filter(skill_level=skill_level)

    if video_type:
        services = services.filter(video_type=video_type)

    if delivery_time:
        services = services.filter(delivery_time=delivery_time)

    if output_format:
        services = services.filter(output_format=output_format)

    if min_price_value is not None:
        # Price is a Decimal in the model, so do not compare it with a float.
        services = services.filter(price__gte=min_price_value)

    if max_price_value is not None:
        services = services.filter(price__lte=max_price_value)

    has_search_criteria = any(
        [
            query,
            analysis_type,
            min_price_value is not None,
            max_price_value is not None,
        ]
    )

    if request.user.is_authenticated and has_search_criteria:
        # Save useful search criteria so the dashboard can recommend related services.
        SearchHistory.objects.create(
            user=request.user,
            query=query,
            analysis_type=analysis_type,
            min_price=min_price_value,
            max_price=max_price_value,
        )

    context = {
        "services": services,
        "categories": Category.objects.all(),
        "subcategories": SubCategory.objects.select_related("category"),
        "analysis_type_choices": Service.AnalysisType.choices,
        "skill_level_choices": Service.SkillLevel.choices,
        "video_type_choices": Service.VideoType.choices,
        "delivery_time_choices": Service.DeliveryTime.choices,
        "output_format_choices": Service.OutputFormat.choices,
        "filters": {
            "q": query,
            "category": category_slug,
            "subcategory": subcategory_slug,
            "analysis_type": analysis_type,
            "skill_level": skill_level,
            "video_type": video_type,
            "delivery_time": delivery_time,
            "output_format": output_format,
            "min_price": min_price,
            "max_price": max_price,
        },
    }
    return render(request, "catalogue/service_list.html", context)


def service_detail(request, slug):
    # Only active services can be opened from the public website.
    service = get_object_or_404(
        Service.objects.select_related("category", "subcategory"),
        slug=slug,
        is_active=True,
    )

    user_rating = None
    in_wishlist = False

    if request.user.is_authenticated:
        # Opening the same service again updates its viewed time instead of adding duplicates.
        RecentlyViewedService.objects.update_or_create(
            user=request.user,
            service=service,
        )
        user_rating = Rating.objects.filter(user=request.user, service=service).first()
        in_wishlist = WishlistItem.objects.filter(
            user=request.user,
            service=service,
        ).exists()

    # Calculate the public rating summary from every user's rating for this service.
    rating_summary = service.ratings.aggregate(average=Avg("score"))
    average_rating = rating_summary["average"] or 0
    rating_count = service.ratings.count()

    # The detail page uses a simple same-category recommendation.
    recommended_services = (
        Service.objects.filter(
            is_active=True,
            category=service.category,
        )
        .exclude(id=service.id)
        .select_related("category", "subcategory")
        .order_by("name")[:3]
    )

    return render(
        request,
        "catalogue/service_detail.html",
        {
            "service": service,
            "recommended_services": recommended_services,
            "average_rating": round(average_rating, 1),
            "rating_count": rating_count,
            "user_rating": user_rating,
            "in_wishlist": in_wishlist,
        },
    )
