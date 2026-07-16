"""Top-level URL routing for ThirdEye.

Feature routes stay inside their app-specific ``urls.py`` files. This file
only joins those route groups and exposes the home and Django Admin pages.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path('', core_views.home, name='home'),
    path('', include('catalogue.urls')),
    path('', include('accounts.urls')),
    path('', include('interactions.urls')),
    path('', include('cart.urls')),
    # This is Django's built-in admin, not the management pages made for the site.
    path('django-admin/', admin.site.urls),
]

# While developing, Django serves uploaded service images from the media folder.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
