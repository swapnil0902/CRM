from django import forms
from .models import Task
from crm_home.models import UserProfile
from customer.models import Customer
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

class TaskForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    due_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Task
        fields = ['client_name', 'title', 'description', 'due_date', 'due_time', 'priority', 'status', 'assigned_to', 'customer']
    

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user') 
        super(TaskForm, self).__init__(*args, **kwargs)

        if user.groups.filter(name='Account Manager').exists():
            user_profile = get_object_or_404(UserProfile, staff=user)
            self.fields['assigned_to'].queryset = User.objects.filter(userprofile__company=user_profile.company)
            self.fields['assigned_to'].required = True  
        else:
            self.fields.pop('assigned_to')

        user_profile = get_object_or_404(UserProfile, staff=user)
        self.fields['customer'].queryset = Customer.objects.filter(company=user_profile.company)


class TaskFilterForm(forms.Form):
    PRIORITY_CHOICES = (
        ('', 'All'),
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )
    STATUS_CHOICES = (
        ('', 'All'),
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )

    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))