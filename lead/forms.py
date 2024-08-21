from django import forms
from django.contrib.auth.models import User
from .models import Lead
from crm_home.models import UserProfile
from django.shortcuts import get_object_or_404


class LeadForm(forms.ModelForm):
    staff = forms.ModelChoiceField(queryset=User.objects.none(), required=False)

    class Meta:
        model = Lead
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')  # Pass the current user as a kwarg when initializing the form
        super(LeadForm, self).__init__(*args, **kwargs)

        if user.groups.filter(name='Account Manager').exists():
            # If the user is an Account Manager, add the staff field
            user_profile = get_object_or_404(UserProfile, staff=user)
            self.fields['staff'].queryset = User.objects.filter(userprofile__company=user_profile.company)
            self.fields['staff'].required = True  # Make the staff field required for Account Managers
        else:
            # If the user is not an Account Manager, remove the staff field
            self.fields.pop('staff')
