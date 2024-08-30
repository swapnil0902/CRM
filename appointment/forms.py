from django import forms
from .models import Appointment
from django.shortcuts import get_object_or_404
from crm_home.models import UserProfile
from customer.models import Customer,User

##################################          #########################################################
class AppointmentForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Appointment
        fields = ['title', 'description', 'start_date', 'end_date', 'location', 'attendees', 'customer']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)

        if user:
            try:
                user_profile = UserProfile.objects.get(staff=user)
                self.fields['customer'].queryset = Customer.objects.filter(company=user_profile.company)
                self.fields['attendees'].queryset = User.objects.filter(userprofile__company=user_profile.company)

                if user.groups.filter(name='Staff').exists():
                    self.fields.pop('attendees')

            except UserProfile.DoesNotExist:
                self.fields['customer'].queryset = Customer.objects.none()
                self.fields['attendees'].queryset = User.objects.none()

##################################          #########################################################

