"""
visits.models

Core data models for the Vendor Visit Calendar application.

This app tracks:
- Vendor companies and contacts
- Site equipment assets or equipment groups
- Scheduled vendor visits
- Pre-visit planning notes
- Post-visit handoff notes for technicians

These models are intentionally structured to support:
- Calendar-based scheduling
- Equipment-level filtering
- Future reporting and analytics
"""

from django.conf import settings
from django.db import models
from django.utils import timezone


class Vendor(models.Model):
    """
    Represents a vendor company that performs work at the site.
    """

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Vendor company name.",
    )

    def __str__(self) -> str:
        return self.name


class VendorContact(models.Model):
    """
    Represents an individual technician or contact from a vendor company.
    """

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="contacts",
        help_text="Vendor company this contact belongs to.",
    )

    name = models.CharField(
        max_length=200,
        help_text="Contact full name.",
    )

    phone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional contact phone number.",
    )

    email = models.EmailField(
        blank=True,
        help_text="Optional contact email address.",
    )

    def __str__(self) -> str:
        return f"{self.vendor.name} - {self.name}"


class Equipment(models.Model):
    """
    Represents a site asset or equipment group that vendors may work on.

    This model is meant to represent an overall group (beds, HVAC units, fans, FLS, etc.)
    rather than individual components (motors, PEs, sensors).

    This allows filtering visits by:
    - Area (AB, EG, HJ, etc.)
    - System type (MHE and Facilities categories)
    """

    AREA_CHOICES = [
        ("AB", "AB"),
        ("EG", "EG"),
        ("HJ", "HJ"),
        ("CD", "CD"),
        ("BLDG", "Building"),
        ("OTHER", "Other"),
    ]

    SYSTEM_CHOICES = [
        # MHE systems
        ("INDUCT", "Induct"),
        ("TSORT", "TSORT"),
        ("ADTA", "ADTA"),
        ("SBL", "SBL"),
        ("MHE_OTHER", "MHE Other"),
        # Facilities / Building systems
        ("HVAC", "HVAC"),
        ("FANS", "Fans"),
        ("FLS", "Fire Life Safety"),
        ("ELECTRICAL", "Electrical"),
        ("PLUMBING", "Plumbing"),
        ("BUILDING", "Building"),
        # Fallback
        ("OTHER", "Other"),
    ]

    area = models.CharField(
        max_length=10,
        choices=AREA_CHOICES,
        default="OTHER",
        help_text="Physical area of the building where the equipment group is located.",
    )

    system = models.CharField(
        max_length=20,
        choices=SYSTEM_CHOICES,
        default="OTHER",
        help_text="System type or equipment category.",
    )

    asset_name = models.CharField(
        max_length=200,
        help_text="Human-readable equipment group name used in UI and communication.",
    )

    asset_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional structured identifier (example AB.ADTA.01).",
    )

    class Meta:
        verbose_name_plural = "Equipment"
        indexes = [
            models.Index(fields=["area", "system"]),
            models.Index(fields=["asset_id"]),
        ]

    def __str__(self) -> str:
        """
        Return a readable equipment label for admin and UI display.

        We prioritize asset_name for readability and append asset_id when present.
        """
        if self.asset_id:
            return f"{self.asset_name} ({self.asset_id})"
        return self.asset_name


class Visit(models.Model):
    """
    Represents a scheduled vendor visit to the site.

    A visit may:
    - Be tied to one vendor
    - Involve multiple equipment groups
    - Have pre-visit notes for planning
    - Have post-visit handoff notes for other technicians
    """

    STATUS_CHOICES = [
        ("SCHEDULED", "Scheduled"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("CANCELED", "Canceled"),
    ]

    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.PROTECT,
        related_name="visits",
        help_text="Vendor company performing the work.",
    )

    contact = models.ForeignKey(
        VendorContact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visits",
        help_text="Primary vendor contact for this visit.",
    )

    title = models.CharField(
        max_length=200,
        help_text="Short summary shown on calendar (example Annual PM or Alignment check).",
    )

    start_dt = models.DateTimeField(
        help_text="Scheduled start date and time.",
    )

    end_dt = models.DateTimeField(
        help_text="Scheduled end date and time.",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="SCHEDULED",
        help_text="Current lifecycle state of the visit.",
    )

    equipment = models.ManyToManyField(
        Equipment,
        blank=True,
        related_name="visits",
        help_text="Equipment groups involved in this visit.",
    )

    work_scope = models.TextField(
        blank=True,
        help_text="Detailed description of work to be performed.",
    )

    sim_ticket = models.CharField(
        max_length=100,
        blank=True,
        help_text="Reference SIM ticket number if applicable.",
    )

    work_order = models.CharField(
        max_length=100,
        blank=True,
        help_text="Internal or vendor work order reference if applicable.",
    )

    pre_visit_notes = models.TextField(
        blank=True,
        help_text="Planning notes, access constraints, staging details, and prep items.",
    )

    post_visit_handoff = models.TextField(
        blank=True,
        help_text="Summary for other technicians after completion including follow ups.",
    )

    site_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_visits",
        help_text="Internal technician responsible for coordination and handoff.",
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the visit record was created.",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the visit record was last updated.",
    )

    class Meta:
        ordering = ["-start_dt"]
        indexes = [
            models.Index(fields=["start_dt", "end_dt"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.vendor.name} - {self.title}"