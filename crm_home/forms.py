import string
import random
from django import forms
from .models import Company,UserProfile,User
from django.contrib.auth.models import User, Group

#####################################        #############################################
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'service']  

    name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Company Name'}),
    )
    service = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Service Provided'}),
    )


#####################################        #############################################
class AccountManagerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    username = forms.CharField(max_length=30, label='Username')
    email = forms.EmailField(label='Email')
    company = forms.ModelChoiceField(queryset=Company.objects.all(), label='Company')

    class Meta:
        model = UserProfile
        fields = ['company']  

    def __init__(self, *args, **kwargs):
        super(AccountManagerForm, self).__init__(*args, **kwargs)
        self.fields['first_name'] = forms.CharField(max_length=30, label='First Name')
        self.fields['last_name'] = forms.CharField(max_length=30, label='Last Name')
        self.fields['username'] = forms.CharField(max_length=30, label='Username')
        self.fields['email'] = forms.EmailField(label='Email')
        self.fields['company'] = forms.ModelChoiceField(queryset=Company.objects.all(), label='Company')

    def generate_password(self, length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(characters) for i in range(length))
    
    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],  
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email']
        )
        password = self.generate_password()
        print(password)
        user.set_password(password)
        if commit:
            user.save()
        
        user_profile = super(AccountManagerForm, self).save(commit=False)
        user_profile.staff = user
        if commit:
            user_profile.save()
        
        account_manager_group = Group.objects.get(name="Account Manager")
        user.groups.add(account_manager_group)

        return user_profile, password
    

#####################################        #############################################
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

#####################################        #############################################