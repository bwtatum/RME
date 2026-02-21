"""
visits.views

Request handlers for the Vendor Visit Calendar.

This module provides:
- Calendar page (HTML UI)
- Create edit detail pages for visits
- JSON endpoint for calendar event retrieval

We keep business logic light in views. If logic grows, we will move it into:
- services.py for domain logic
- selectors.py for query construction
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_datetime

from .forms import VisitForm
from .models import Visit


@login_required
def calendar_view(request: HttpRequest) -> HttpResponse:
    """
    Render the main calendar UI page.

    The page itself loads events via the visit_events JSON endpoint.
    """
    return render(request, "visits/calendar.html")


@login_required
def visit_create(request: HttpRequest) -> HttpResponse:
    """
    Create a new vendor visit.

    GET shows a blank form.
    POST validates and saves then redirects to the visit detail page.
    """
    if request.method == "POST":
        form = VisitForm(request.POST)
        if form.is_valid():
            visit = form.save()
            return redirect("visit_detail", pk=visit.pk)
    else:
        form = VisitForm()

    return render(request, "visits/visit_form.html", {"form": form, "mode": "create"})


@login_required
def visit_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Display a single visit and all related information.
    """
    visit = get_object_or_404(Visit, pk=pk)
    return render(request, "visits/visit_detail.html", {"visit": visit})


@login_required
def visit_edit(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Edit an existing vendor visit.
    """
    visit = get_object_or_404(Visit, pk=pk)

    if request.method == "POST":
        form = VisitForm(request.POST, instance=visit)
        if form.is_valid():
            form.save()
            return redirect("visit_detail", pk=visit.pk)
    else:
        form = VisitForm(instance=visit)

    return render(
        request,
        "visits/visit_form.html",
        {"form": form, "mode": "edit", "visit": visit},
    )


@login_required
def visit_events(request: HttpRequest) -> JsonResponse:
    """
    Return visit events as JSON for FullCalendar.

    FullCalendar passes start and end query params which define the visible range.
    We also support basic filters to help techs find what matters quickly:
    - vendor_id: only visits for one vendor
    - status: scheduled, in progress, completed, canceled
    - area: AB, EG, etc (via equipment)
    - system: induct, tsort, etc (via equipment)

    Output format must match FullCalendar expected fields.
    """
    start = request.GET.get("start")
    end = request.GET.get("end")

    qs = Visit.objects.select_related("vendor").prefetch_related("equipment").all()

    # Range filtering: include visits that overlap the visible window
    if start:
        start_dt = parse_datetime(start)
        if start_dt:
            qs = qs.filter(end_dt__gte=start_dt)
    if end:
        end_dt = parse_datetime(end)
        if end_dt:
            qs = qs.filter(start_dt__lte=end_dt)

    # Optional filters
    vendor_id = request.GET.get("vendor_id")
    if vendor_id:
        qs = qs.filter(vendor_id=vendor_id)

    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)

    area = request.GET.get("area")
    if area:
        qs = qs.filter(equipment__area=area).distinct()

    system = request.GET.get("system")
    if system:
        qs = qs.filter(equipment__system=system).distinct()

    # Convert visits to FullCalendar event objects
    events = []
    for v in qs:
        # Short equipment labels for calendar readability
        equipment_labels = [e.asset_name for e in v.equipment.all()]
        equip_text = ", ".join(equipment_labels[:2])
        if len(equipment_labels) > 2:
            equip_text = f"{equip_text} +{len(equipment_labels) - 2}"

        # Title format: Vendor first, then what, then equipment group
        # Example: Raymond West | Forklift PM | AB Aligner Bed
        title_parts = [v.vendor.name, v.title]
        if equip_text:
            title_parts.append(equip_text)

        calendar_title = " | ".join(title_parts)

        # Status based coloring for quick scanning
        status_colors = {
            "SCHEDULED": "#1d4ed8",    # blue
            "IN_PROGRESS": "#f59e0b",  # amber
            "COMPLETED": "#16a34a",    # green
            "CANCELED": "#6b7280",     # gray
        }

        events.append(
            {
                "id": v.pk,
                "title": calendar_title,
                "start": v.start_dt.isoformat(),
                "end": v.end_dt.isoformat(),
                "url": f"/visits/{v.pk}/",
                "backgroundColor": status_colors.get(v.status, "#1d4ed8"),
                "borderColor": status_colors.get(v.status, "#1d4ed8"),
            }
        )

    return JsonResponse(events, safe=False)