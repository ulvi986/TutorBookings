from django import forms

from apps.tutors.models import AvailabilitySlot, Subject

from .models import Booking


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["slot", "subject", "notes"]

    def __init__(self, *args, tutor_profile=None, **kwargs):
        super().__init__(*args, **kwargs)
        if tutor_profile is not None:
            self.fields["slot"].queryset = AvailabilitySlot.objects.filter(
                tutor_profile=tutor_profile,
                is_active=True,
                booking__isnull=True,
            )
            self.fields["subject"].queryset = Subject.objects.filter(tutorprofile=tutor_profile)
