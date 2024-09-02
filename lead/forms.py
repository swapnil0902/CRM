from django import forms
from .models import Lead
from crm_home.models import UserProfile
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


class LeadForm(forms.ModelForm):
    staff = forms.ModelChoiceField(queryset=User.objects.none(), required=False)

    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user') 
        super(LeadForm, self).__init__(*args, **kwargs)

        if user.groups.filter(name='Account Manager').exists():
            user_profile = get_object_or_404(UserProfile, staff=user)
            self.fields['staff'].queryset = User.objects.filter(userprofile__company=user_profile.company)
            self.fields['staff'].required = True  
        else:
            self.fields.pop('staff')

