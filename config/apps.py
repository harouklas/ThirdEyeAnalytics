"""Application configuration for the Head Administrator-only Django Admin."""

from django.contrib.admin.apps import AdminConfig


class HeadAdministratorAdminConfig(AdminConfig):
    default_site = "config.admin_site.HeadAdministratorAdminSite"
