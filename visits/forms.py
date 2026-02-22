"""
visits.forms

Forms used for creating and editing vendor visits.

We use ModelForm because it provides:
- Validation tied to model fields
- Less duplicated field definitions
- Easier maintenance when models change

We can later add custom validation here, such as:
- End time must be after start time
- Required equipment for certain visit types
"""

from django import forms
from .models import Visit


class VisitForm(forms.ModelForm):
    """
    Form used to create or edit a Visit.

    We use datetime-local inputs so users can schedule quickly in browser.
    Django expects naive datetimes here; timezone behavior is handled by settings.
    """

    class Meta:
        model = Visit
        fields = [
            "vendor",
            "contact",
            "title",
            "start_dt",
            "end_dt",
            "status",
            "equipment",
            "work_scope",
            "sim_ticket",
            "work_order",
            "pre_visit_notes",
            "post_visit_handoff",
            "site_owner",
        ]
        widgets = {
            # datetime-local renders a native date/time picker in most browsers
            "start_dt": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_dt": forms.DateTimeInput(attrs={"type": "datetime-local"}),

            # multi-select made readable without requiring extra UI libraries
            "equipment": forms.SelectMultiple(attrs={"size": 6}),
        }

    def clean(self):
        """
        Enforce basic scheduling integrity.

        This prevents common mistakes like end time before start time.
        """
        cleaned = super().clean()
        start_dt = cleaned.get("start_dt")
        end_dt = cleaned.get("end_dt")

        if start_dt and end_dt and end_dt <= start_dt:
            self.add_error("end_dt", "End time must be after start time.")

        return cleaned