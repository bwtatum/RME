"""
visits.urls

URL routes for Vendor Visit Calendar.
"""

from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("visits/new/", views.visit_create, name="visit_create"),
    path("visits/<int:pk>/", views.visit_detail, name="visit_detail"),
    path("visits/<int:pk>/edit/", views.visit_edit, name="visit_edit"),
    path("visits/events/", views.visit_events, name="visit_events"),
]