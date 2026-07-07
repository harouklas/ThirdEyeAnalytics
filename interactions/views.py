from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from catalogue.models import Service

from .models import Rating, WishlistItem


@login_required
@require_POST
def toggle_wishlist(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)
    wishlist_item, created = WishlistItem.objects.get_or_create(
        user=request.user,
        service=service,
    )

    if not created:
        wishlist_item.delete()

    return JsonResponse(
        {
            "in_wishlist": created,
            "wishlist_count": service.wishlisted_by.count(),
        }
    )


@login_required
@require_POST
def rate_service(request, service_id):
    service = get_object_or_404(Service, id=service_id, is_active=True)

    try:
        score = int(request.POST.get("score", "0"))
    except ValueError:
        score = 0

    if score < 1 or score > 5:
        return JsonResponse({"error": "Rating must be from 1 to 5."}, status=400)

    Rating.objects.update_or_create(
        user=request.user,
        service=service,
        defaults={"score": score},
    )

    rating_summary = service.ratings.aggregate(average=Avg("score"))
    average_rating = rating_summary["average"] or 0

    return JsonResponse(
        {
            "score": score,
            "average_rating": round(average_rating, 1),
            "rating_count": service.ratings.count(),
        }
    )
