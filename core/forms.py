from django import forms
from .models import ClinicSchedule


class ClinicScheduleForm(forms.ModelForm):

    start_time = forms.TimeField(
        input_formats=['%I:%M %p']
    )

    end_time = forms.TimeField(
        input_formats=['%I:%M %p']
    )

    class Meta:
        model = ClinicSchedule
        fields = ['day', 'start_time', 'end_time']