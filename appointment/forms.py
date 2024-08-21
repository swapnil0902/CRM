from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Appointment
        fields = ['title','description','start_date','end_date','location','attendees','customer']
        