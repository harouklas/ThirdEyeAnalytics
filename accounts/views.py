"""Views for authentication, profile pages, dashboards, and staff management."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

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
    # Put the staff check in one decorator so every management page uses it.
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
            # User stores login details; Profile stores the extra football details.
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.save()

            Profile.objects.create(
                user=user,
                full_name=f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}",
                phone_country_code=form.cleaned_data["phone_country_code"],
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
    # A superuser made with createsuperuser may not have a Profile yet.
    profile, _created = Profile.objects.get_or_create(
        user=request.user,
        defaults={"full_name": request.user.username},
    )
    # Show only the latest activity so the dashboard stays simple.
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
    user_ratings = (
        Rating.objects.filter(user=request.user)
        .select_related("service")
        .order_by("-updated_at")[:5]
    )
    # Recommendations are calculated from this user's searches, views, and wishlist.
    recommended_services, latest_search = get_dashboard_recommendations(request.user)

    return render(
        request,
        "accounts/dashboard.html",
        {
            "profile": profile,
            "recent_views": recent_views,
            "wishlist_items": wishlist_items,
            "recent_orders": recent_orders,
            "user_ratings": user_ratings,
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
        # instance=profile updates the existing row instead of creating a new one.
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
    # These totals give staff a quick summary of the website data.
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
        # request.FILES contains the optional uploaded service image.
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
        # Passing the service instance changes this service instead of adding another one.
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
def management_service_delete(request, service_id):
    """Show a confirmation page and delete the service only after a POST."""

    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        service_name = service.name
        service_image = service.image
        try:
            service.delete()
        except ProtectedError:
            # OrderItem uses PROTECT so completed order history is never damaged.
            messages.error(
                request,
                f"{service_name} cannot be deleted because it is part of a saved order. "
                "Edit the service and hide it instead.",
            )
        else:
            # Remove an uploaded image after the database deletion succeeds.
            if service_image:
                service_image.delete(save=False)
            messages.success(request, f"{service_name} has been deleted.")
        return redirect("accounts:management_services")

    return render(
        request,
        "accounts/management_confirm_delete.html",
        {
            "page_title": "Delete service",
            "object_type": "service",
            "object_name": service.name,
            "cancel_url": "accounts:management_services",
            "warning": "This also removes its ratings, wishlist entries and cart entries.",
        },
    )


@staff_required
def management_categories(request):
    category_form = CategoryManagementForm()
    subcategory_form = SubCategoryManagementForm()

    if request.method == "POST":
        # Both forms post here, so form_type says which one should be checked.
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
def management_category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        # instance tells ModelForm to update this category instead of adding one.
        form = CategoryManagementForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            messages.success(request, f"{category.name} category has been updated.")
            return redirect("accounts:management_categories")
    else:
        form = CategoryManagementForm(instance=category)

    return render(
        request,
        "accounts/management_category_form.html",
        {
            "form": form,
            "page_title": "Edit category",
            "item_type": "category",
        },
    )


@staff_required
def management_subcategory_edit(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    if request.method == "POST":
        # The form also checks the selected parent category and unique slug.
        form = SubCategoryManagementForm(request.POST, instance=subcategory)
        if form.is_valid():
            subcategory = form.save()
            messages.success(request, f"{subcategory.name} sub-category has been updated.")
            return redirect("accounts:management_categories")
    else:
        form = SubCategoryManagementForm(instance=subcategory)

    return render(
        request,
        "accounts/management_category_form.html",
        {
            "form": form,
            "page_title": "Edit sub-category",
            "item_type": "sub-category",
        },
    )


@staff_required
def management_category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == "POST":
        category_name = category.name
        try:
            category.delete()
        except ProtectedError:
            # Service.category uses PROTECT so a category in use stays available.
            messages.error(
                request,
                f"{category_name} cannot be deleted because it or one of its "
                "sub-categories is used by a service.",
            )
        else:
            messages.success(request, f"{category_name} category has been deleted.")
        return redirect("accounts:management_categories")

    return render(
        request,
        "accounts/management_confirm_delete.html",
        {
            "page_title": "Delete category",
            "object_type": "category",
            "object_name": category.name,
            "cancel_url": "accounts:management_categories",
            "warning": "Its sub-categories will also be deleted if none are in use.",
        },
    )


@staff_required
def management_subcategory_delete(request, subcategory_id):
    subcategory = get_object_or_404(SubCategory, id=subcategory_id)

    if request.method == "POST":
        subcategory_name = subcategory.name
        try:
            subcategory.delete()
        except ProtectedError:
            # Service.subcategory uses PROTECT so linked services are not broken.
            messages.error(
                request,
                f"{subcategory_name} cannot be deleted because it is used by a service.",
            )
        else:
            messages.success(
                request,
                f"{subcategory_name} sub-category has been deleted.",
            )
        return redirect("accounts:management_categories")

    return render(
        request,
        "accounts/management_confirm_delete.html",
        {
            "page_title": "Delete sub-category",
            "object_type": "sub-category",
            "object_name": subcategory.name,
            "cancel_url": "accounts:management_categories",
            "warning": "This action cannot be undone.",
        },
    )


@staff_required
def management_users(request):
    # Ensure accounts created with createsuperuser also have a Profile record.
    for user_obj in User.objects.all():
        if user_obj.is_superuser:
            default_role = Profile.UserRole.HEAD_ADMINISTRATOR
        elif user_obj.is_staff:
            default_role = Profile.UserRole.ADMINISTRATOR
        else:
            default_role = Profile.UserRole.USER

        profile, _created = Profile.objects.get_or_create(
            user=user_obj,
            defaults={
                "full_name": user_obj.username,
                "role": default_role,
            },
        )

        # Django's staff flags control access, so the displayed role must match them.
        if user_obj.is_staff and profile.role != default_role:
            profile.role = default_role
            profile.save(update_fields=["role"])

    users = User.objects.select_related("profile").order_by("username")
    return render(
        request,
        "accounts/management_users.html",
        {
            "users": users,
            "role_choices": Profile.UserRole.choices,
        },
    )


@staff_required
@require_POST
def management_user_role_update(request, user_id):
    """Let only a Head Administrator change another account's access role."""

    # Staff can view users, but only a Head Administrator can change access roles.
    if not request.user.is_superuser:
        messages.error(request, "Only a Head Administrator can change user roles.")
        return redirect("accounts:management_users")

    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot change your own Head Administrator role.")
        return redirect("accounts:management_users")

    selected_role = request.POST.get("role", "")
    # Accept only one of the role values defined by Profile.UserRole.
    valid_roles = {value for value, _label in Profile.UserRole.choices}
    if selected_role not in valid_roles:
        messages.error(request, "Please select a valid role.")
        return redirect("accounts:management_users")

    profile, _created = Profile.objects.get_or_create(
        user=target_user,
        defaults={"full_name": target_user.username},
    )
    profile.role = selected_role
    profile.save(update_fields=["role"])

    # Save the displayed role and the real Django permission flags together.
    target_user.is_superuser = selected_role == Profile.UserRole.HEAD_ADMINISTRATOR
    target_user.is_staff = selected_role in {
        Profile.UserRole.HEAD_ADMINISTRATOR,
        Profile.UserRole.ADMINISTRATOR,
    }
    target_user.save(update_fields=["is_superuser", "is_staff"])

    messages.success(
        request,
        f"{target_user.username} is now a {profile.get_role_display()}.",
    )
    return redirect("accounts:management_users")
