import string
import random
from django import forms
from crm_home.models import Company
from .models import UserRequest,CompanyRequest
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group, Permission,User


#####################################        #############################################
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

            group = self.cleaned_data['group']
            user.groups.add(group)
            
        return user, password

    
#####################################        #############################################

class UserRequestForm(forms.ModelForm):
    company = forms.ModelChoiceField(queryset=Company.objects.all(), empty_label="Select a Company")

    class Meta:
        model = UserRequest
        fields = ['first_name', 'last_name', 'email','company' ]

#####################################        #############################################

class CompanyRequestForm(forms.ModelForm):
    class Meta:
        model = CompanyRequest
        fields = ['name', 'service', 'description']

#####################################        #############################################

class CustomAuthenticationForm(AuthenticationForm):
    pass


##################################          ###############################################
class UsernamePasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150, required=True, label='Username')


##################################          ###############################################
class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label='OTP')


##################################          ################################################
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, required=True, label='New Password')
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True, label='Confirm Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')

##################################          #################################################