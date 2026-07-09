from decimal import Decimal, InvalidOperation

from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, render

from interactions.models import Rating, RecentlyViewedService, SearchHistory, WishlistItem

from .models import Category, Service, SubCategory


def service_list(request):
    services = (
        Service.objects.filter(is_active=True)
        .select_related("category", "subcategory")
        .order_by("name")
    )

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "")
    subcategory_slug = request.GET.get("subcategory", "")
    analysis_type = request.GET.get("analysis_type", "")
    skill_level = request.GET.get("skill_level", "")
    video_type = request.GET.get("video_type", "")
    delivery_time = request.GET.get("delivery_time", "")
    output_format = request.GET.get("output_format", "")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    min_price_value = None
    max_price_value = None

    if query:
        services = services.filter(
            Q(name__icontains=query)
            | Q(short_description__icontains=query)
            | Q(description__icontains=query)
        )

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

    if min_price:
        try:
            min_price_value = Decimal(min_price)
            services = services.filter(price__gte=min_price_value)
        except InvalidOperation:
            pass

    if max_price:
        try:
            max_price_value = Decimal(max_price)
            services = services.filter(price__lte=max_price_value)
        except InvalidOperation:
            pass

    has_search_criteria = any(
        [
            query,
            analysis_type,
            min_price_value is not None,
            max_price_value is not None,
        ]
    )

    if request.user.is_authenticated and has_search_criteria:
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
    service = get_object_or_404(
        Service.objects.select_related("category", "subcategory"),
        slug=slug,
        is_active=True,
    )

    user_rating = None
    in_wishlist = False

    if request.user.is_authenticated:
        RecentlyViewedService.objects.update_or_create(
            user=request.user,
            service=service,
        )
        user_rating = Rating.objects.filter(user=request.user, service=service).first()
        in_wishlist = WishlistItem.objects.filter(
            user=request.user,
            service=service,
        ).exists()

    rating_summary = service.ratings.aggregate(average=Avg("score"))
    average_rating = rating_summary["average"] or 0
    rating_count = service.ratings.count()

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
