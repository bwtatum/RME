"""
config.urls

Top level URL routing for the project.

We keep routing clean and minimal here:
- Admin interface
- Auth routes (login logout password reset)
- App routes for the visits calendar
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Django built-in auth pages (login logout password reset)
    path("accounts/", include("django.contrib.auth.urls")),

    # Main application routes
    path("", include("visits.urls")),
]