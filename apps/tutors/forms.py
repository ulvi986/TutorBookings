from django import forms

from .models import AvailabilitySlot, TutorProfile


class TutorProfileForm(forms.ModelForm):
    class Meta:
        model = TutorProfile
        fields = ["bio", "education", "hourly_rate", "profile_photo", "subjects"]
        widgets = {"subjects": forms.CheckboxSelectMultiple}


class AvailabilitySlotForm(forms.ModelForm):
    class Meta:
        model = AvailabilitySlot
        fields = ["start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
