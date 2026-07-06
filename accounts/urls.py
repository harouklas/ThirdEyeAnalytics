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
]
