from django import forms
from django.contrib.auth.models import Group, Permission,User
import string
import random
from django.core.exceptions import ValidationError

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


class SignUpForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, label="Select Group")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

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
        return user, password  # Return the user and the generated password



from django.contrib.auth.forms import PasswordChangeForm

class ActivatePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput, label='Old Password')
    new_password1 = forms.CharField(widget=forms.PasswordInput, label='New Password')
    new_password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm New Password')

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")

        return cleaned_data
    
from django import forms
from .models import CustomerRequest

class CustomerRequestForm(forms.ModelForm):
    class Meta:
        model = CustomerRequest
        fields = ['first_name', 'last_name', 'email','mobile' ]


