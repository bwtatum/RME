"""
visits.admin

Admin configuration for Vendor Visit Calendar models.
Provides filtering and search for easier data management.
"""

from django.contrib import admin
from .models import Vendor, VendorContact, Equipment, Visit


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(VendorContact)
class VendorContactAdmin(admin.ModelAdmin):
    list_display = ["vendor", "name", "phone", "email"]
    search_fields = ["vendor__name", "name", "email"]


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ["area", "system", "asset_name", "asset_id"]
    list_filter = ["area", "system"]
    search_fields = ["asset_name", "asset_id"]


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ["vendor", "title", "start_dt", "end_dt", "status", "site_owner"]
    list_filter = ["status", "vendor"]
    search_fields = ["title", "vendor__name", "sim_ticket", "work_order"]
    filter_horizontal = ["equipment"]