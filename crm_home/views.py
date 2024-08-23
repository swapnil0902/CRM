from django.shortcuts import render,redirect
from .forms import CompanyForm, UserUpdateForm
from .models import Company
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import UserChangeForm

from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .forms import AccountManagerForm

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from account.forms import CompanyRequestForm
from account.models import CompanyRequest

from django.shortcuts import render, redirect, get_object_or_404
from .forms import CompanyForm  # Ensure this form corresponds to the Company model
from .models import Company

# Create your views here.

def home(request):
    return render(request,"crm_home/index.html")

def dashboard(request):
    return render(request, "crm/dashboard.html")

def my_profile(request):
    return render(request,"crm_home/my_profile.html")

def update_user_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_page')  # Redirect to the profile page or wherever you prefer
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'crm_home/update_profile.html', {'form': form})





@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  
    else:
        form = UserChangeForm(instance=request.user)
    
    editable = 'edit' in request.GET
    return render(request, 'crm_home/my_profile.html', {'form': form, 'editable': editable})

def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list') 
    else:
        form = CompanyForm()
    
    return render(request, 'crm_home/create_company.html', {'form': form})



def prefilled_create_company(request, request_id=None):
    # Check if there is a request_id to prefill the form
    if request_id:
        # Fetch the Company object based on request_id
        company = get_object_or_404(CompanyRequest, pk=request_id)
        initial_data = {
            'name': company_request.name,
            'service': company_request.service,
        }
    else:
        initial_data = {}

    print(initial_data)  

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            # Save the new company
            form.save()
            return redirect('company_list')  # Redirect to a success page or list of companies
        else:
            return render(request, 'crm_home/create_company.html', {'form': form})
    
    else:
        form = CompanyForm(initial=initial_data)

    return render(request, 'crm_home/create_company.html', {'form': form})


def company_list(request):
    companies = Company.objects.all()
    return render(request, 'crm_home/company_list.html', {'companies': companies})


def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    users = company.users.all()

    if request.method == 'POST':
        form = AccountManagerForm(request.POST)
        if form.is_valid():
            user_profile, password = form.save()  

           
            html_message = render_to_string(
                'account/email_template.html',
                {
                    'first_name': user_profile.staff.first_name,
                    'username': user_profile.staff.username,
                    'password': password,
                    'support_email': 'sivatejat509@gmail.com',
                    'login_url': 'http://localhost:8000/login/',  
                }
            )
            plain_message = strip_tags(html_message)

           
            send_mail(
                'Your Account Details and Instructions',
                plain_message,
                'sivatejat509@gmail.com',  
                [user_profile.staff.email],
                fail_silently=False,
                html_message=html_message,
            )

            return redirect('company_detail', pk=company.pk)
    else:
        form = AccountManagerForm(initial={'company': company})

    return render(request, 'crm_home/company_detail.html', {
        'company': company,
        'users': users,
        'form': form
    })
