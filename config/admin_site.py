"""Django Admin setup that only accepts Head Administrator accounts."""

from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.core.exceptions import ValidationError


class HeadAdministratorAuthenticationForm(AdminAuthenticationForm):
    """Reject staff credentials unless the account is a Head Administrator."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_superuser:
            raise ValidationError(
                "Only Head Administrators can access advanced administration.",
                code="head_administrator_only",
            )


class HeadAdministratorAdminSite(AdminSite):
    """Keep Django Admin separate from the management pages used by all staff."""

    site_header = "ThirdEye Head Administration"
    site_title = "ThirdEye Admin"
    index_title = "Advanced administration"
    site_url = None
    login_form = HeadAdministratorAuthenticationForm

    def has_permission(self, request):
        user = request.user
        return user.is_active and user.is_staff and user.is_superuser
