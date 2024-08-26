import string
import random
from django import forms
from crm_home.models import Company
from django.core.exceptions import ValidationError
from .models import UserRequest,CompanyRequest
from django.contrib.auth.models import Group, Permission,User
from django.contrib.auth.forms import AuthenticationForm

#####################################        #############################################
from django import forms
from .models import UserRequest,CompanyRequest
from crm_home.models import Company,UserProfile

class GroupForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if Group.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Group with this Name already exists.')
        return name

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['permissions'].initial = self.instance.permissions.all()

#####################################        #############################################

class SignUpForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Select Group")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username']

    def generate_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.generate_password()
        user.set_password(password)
        if commit:
            user.save()

            # Save UserProfile with company association
            group = self.cleaned_data['group']
            user.groups.add(group)
            
        
        return user, password
    


# class SignUpForm(forms.ModelForm):
#     group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Select Group")
#     company = forms.ModelChoiceField(queryset=Company.objects.all(), required=True, label="Select Company")

#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email', 'username']

#     def generate_password(self, length=12):
#         characters = string.ascii_letters + string.digits + string.punctuation
#         return ''.join(random.choice(characters) for i in range(length))

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         password = self.generate_password()
#         user.set_password(password)
        
#         if commit:
#             user.save()

#             # Assign selected group to user
#             group = self.cleaned_data['group']
#             user.groups.add(group)

#             # Assign selected company and create UserProfile
#             company = self.cleaned_data['company']
#             UserProfile.objects.create(
#                 staff=user,
#                 company=company
#             )
        
#         return user, password


#####################################        #############################################

    
#####################################        #############################################


# class CustomerRequestForm(forms.ModelForm):
#     company = forms.ModelChoiceField(queryset=Company.objects.all(), label="Select a Company")

#     class Meta:
#         model = CustomerRequest
#         fields = ['first_name', 'last_name', 'email','mobile','company' ]


class UserRequestForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label="Select a Company")

    class Meta:
        model = UserRequest
        fields = ['first_name', 'last_name', 'email','mobile','company' ]

#####################################        #############################################

class CompanyRequestForm(forms.ModelForm):
    class Meta:
        model = CompanyRequest
        fields = ['name', 'service', 'description']

#####################################        #############################################


class CustomAuthenticationForm(AuthenticationForm):
    # Add custom fields or override methods if needed
    pass