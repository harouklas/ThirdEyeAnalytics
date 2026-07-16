"""URL routes for registration, login, dashboard, profile, and management pages."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # These routes can be opened before login.
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.UserLoginView.as_view(), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    # The views behind these routes use login_required.
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/profile/", views.profile_edit, name="profile_edit"),
    # staff_required protects this whole group of management views.
    path("management/", views.management_dashboard, name="management_dashboard"),
    path("management/services/", views.management_service_list, name="management_services"),
    path("management/services/add/", views.management_service_add, name="management_service_add"),
    path(
        "management/services/<int:service_id>/edit/",
        views.management_service_edit,
        name="management_service_edit",
    ),
    path(
        "management/services/<int:service_id>/delete/",
        views.management_service_delete,
        name="management_service_delete",
    ),
    path("management/categories/", views.management_categories, name="management_categories"),
    path(
        "management/categories/<int:category_id>/edit/",
        views.management_category_edit,
        name="management_category_edit",
    ),
    path(
        "management/categories/<int:category_id>/delete/",
        views.management_category_delete,
        name="management_category_delete",
    ),
    path(
        "management/sub-categories/<int:subcategory_id>/edit/",
        views.management_subcategory_edit,
        name="management_subcategory_edit",
    ),
    path(
        "management/sub-categories/<int:subcategory_id>/delete/",
        views.management_subcategory_delete,
        name="management_subcategory_delete",
    ),
    path("management/users/", views.management_users, name="management_users"),
    # Changing a role also has an extra Head Administrator check inside the view.
    path(
        "management/users/<int:user_id>/role/",
        views.management_user_role_update,
        name="management_user_role_update",
    ),
]
