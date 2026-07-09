from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("accounts/register/", views.register, name="register"),
    path("accounts/login/", views.UserLoginView.as_view(), name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/profile/", views.profile_edit, name="profile_edit"),
    path("management/", views.management_dashboard, name="management_dashboard"),
    path("management/services/", views.management_service_list, name="management_services"),
    path("management/services/add/", views.management_service_add, name="management_service_add"),
    path(
        "management/services/<int:service_id>/edit/",
        views.management_service_edit,
        name="management_service_edit",
    ),
    path("management/categories/", views.management_categories, name="management_categories"),
    path("management/users/", views.management_users, name="management_users"),
]
