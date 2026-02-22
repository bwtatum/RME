"""
visits.apps

Django application configuration for the visits app.
Keeping this explicit makes it easier to add startup hooks later
(signals, caching, integrations, etc.) without hunting.
"""

from django.apps import AppConfig


class VisitsConfig(AppConfig):
    """
    AppConfig for vendor visit tracking.

    default_auto_field keeps primary keys consistent with modern Django defaults.
    name defines the Python path Django uses to locate the app.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "visits"