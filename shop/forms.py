from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget
from django import forms
from .models import ClashTournament
from datetime import time
from django.utils.dateparse import parse_time

from django.forms.widgets import SplitDateTimeWidget


class ClashTournamentForm(forms.ModelForm):
    class Meta:
        model = ClashTournament
        fields = '__all__'

    def clean_time(self):
        value = self.cleaned_data['time']
        if not (0 <= value <= 2359):
            raise forms.ValidationError("Time must be between 0000 and 2359.")
        hh = value // 100
        mm = value % 100
        if hh > 23 or mm > 59:
            raise forms.ValidationError("Invalid hour or minute in time.")
        return value
