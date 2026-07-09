from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from cart.models import Order
from catalogue.forms import (
    CategoryManagementForm,
    ServiceManagementForm,
    SubCategoryManagementForm,
)
from catalogue.models import Category, Service, SubCategory
from catalogue.recommendations import get_dashboard_recommendations
from interactions.models import Rating, RecentlyViewedService, WishlistItem

from .forms import ProfileForm, RegistrationForm
from .models import Profile

User = get_user_model()


def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Only staff users can open the management area.")
            return redirect("accounts:dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()

            Profile.objects.create(
                user=user,
                full_name=form.cleaned_data["full_name"],
                phone_number=form.cleaned_data["phone_number"],
                organization=form.cleaned_data["organization"],
                sport_role=form.cleaned_data["sport_role"],
                favorite_analysis_type=form.cleaned_data["favorite_analysis_type"],
                bio=form.cleaned_data["bio"],
            )

            login(request, user)
            messages.success(request, "Your account has been created.")
            return redirect("accounts:dashboard")
    else:
        form = RegistrationForm()

    return render(request, "accounts/register.html", {"form": form})


@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("home")

    return redirect("accounts:dashboard")


@login_required
def dashboard(request):
    profile, _created = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.username},
    )
    recent_views = (
        RecentlyViewedService.objects.filter(user=request.user)
        .select_related("service", "service__category")
        .order_by("-viewed_at")[:5]
    )
    wishlist_items = (
        WishlistItem.objects.filter(user=request.user)
        .select_related("service", "service__category")
        .order_by("-created_at")[:5]
    )
    recent_orders = Order.objects.filter(user=request.user).order_by("-created_at")[:5]
    recommended_services, latest_search = get_dashboard_recommendations(request.user)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "profile": profile,
            "recent_views": recent_views,
            "wishlist_items": wishlist_items,
            "recent_orders": recent_orders,
            "recommended_services": recommended_services,
            "latest_search": latest_search,
        },
    )


@login_required
def profile_edit(request):
    profile, _created = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.username},
    )

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:dashboard")
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, "accounts/profile_edit.html", {"form": form})


@staff_required
def management_dashboard(request):
    stats = {
        "services": Service.objects.count(),
        "categories": Category.objects.count(),
        "users": User.objects.count(),
        "orders": Order.objects.count(),
        "ratings": Rating.objects.count(),
    }
    latest_services = Service.objects.select_related("category").order_by("-created_at")[:5]
    latest_orders = Order.objects.select_related("user").order_by("-created_at")[:5]

    return render(
        request,
        "accounts/management_dashboard.html",
        {
            "stats": stats,
            "latest_services": latest_services,
            "latest_orders": latest_orders,
        },
    )


@staff_required
def management_service_list(request):
    services = Service.objects.select_related("category", "subcategory").order_by(
        "category__name",
        "name",
    )
    return render(request, "accounts/management_services.html", {"services": services})


@staff_required
def management_service_add(request):
    if request.method == "POST":
        form = ServiceManagementForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"{service.name} has been added.")
            return redirect("accounts:management_services")
    else:
        form = ServiceManagementForm()

    return render(
        request,
        "accounts/management_service_form.html",
        {
            "form": form,
            "page_title": "Add service",
        },
    )


@staff_required
def management_service_edit(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        form = ServiceManagementForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"{service.name} has been updated.")
            return redirect("accounts:management_services")
    else:
        form = ServiceManagementForm(instance=service)

    return render(
        request,
        "accounts/management_service_form.html",
        {
            "form": form,
            "page_title": "Edit service",
            "service": service,
        },
    )


@staff_required
def management_categories(request):
    category_form = CategoryManagementForm()
    subcategory_form = SubCategoryManagementForm()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "category":
            category_form = CategoryManagementForm(request.POST)
            if category_form.is_valid():
                category = category_form.save()
                messages.success(request, f"{category.name} category has been added.")
                return redirect("accounts:management_categories")

        if form_type == "subcategory":
            subcategory_form = SubCategoryManagementForm(request.POST)
            if subcategory_form.is_valid():
                subcategory = subcategory_form.save()
                messages.success(request, f"{subcategory.name} sub-category has been added.")
                return redirect("accounts:management_categories")

    categories = Category.objects.prefetch_related("subcategories").order_by("name")

    return render(
        request,
        "accounts/management_categories.html",
        {
            "categories": categories,
            "category_form": category_form,
            "subcategory_form": subcategory_form,
        },
    )


@staff_required
def management_users(request):
    users = User.objects.select_related("profile").order_by("username")
    return render(request, "accounts/management_users.html", {"users": users})
