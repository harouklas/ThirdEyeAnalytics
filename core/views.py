"""Views for shared public pages."""

from django.shortcuts import render

from catalogue.models import Category, Service


def home(request):
    # Load the category structure and the services selected for the home page.
    categories = Category.objects.prefetch_related("subcategories")
    featured_services = (
        Service.objects.filter(is_active=True, is_featured=True)
        .select_related("category", "subcategory")
        .order_by("name")[:4]
    )

    return render(
        request,
        "core/home.html",
        {
            "categories": categories,
            "featured_services": featured_services,
        },
    )
