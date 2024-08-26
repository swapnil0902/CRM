from .models import Company
from django.core.mail import send_mail
from django.utils.html import strip_tags
from account.models import CompanyRequest
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CompanyForm,AccountManagerForm,CompanyForm,UserUpdateForm
from django.db.models import Q
from task.models import Task
from appointment.models import Appointment
from customer.models import Customer
from lead.models import Lead
  

# Create your views here.
########################         ##########################################
def home(request):
    return render(request,"crm_home/index.html")


########################         ##########################################
def dashboard(request):
    return render(request, "crm/dashboard.html")


########################         ##########################################
def my_profile(request):
    return render(request,"crm_home/my_profile.html")


########################         ##########################################
def update_user_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_page')  
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'crm_home/update_profile.html', {'form': form})


########################         ##########################################
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list') 
    else:
        form = CompanyForm()

    return render(request, 'crm_home/create_company.html', {'form': form})


########################         ##########################################
def prefilled_create_company(request, request_id=None):
    if request_id:
        company = get_object_or_404(CompanyRequest, pk=request_id)
        initial_data = {
            'name': company.name,
            'service': company.service,
        }
    else:
        initial_data = {}

    print(initial_data)  

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list') 
        else:
            return render(request, 'crm_home/create_company.html', {'form': form})
    
    else:
        form = CompanyForm(initial=initial_data)

    return render(request, 'crm_home/create_company.html', {'form': form})


########################         ##########################################
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'crm_home/company_list.html', {'companies': companies})


########################         ##########################################
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
########################         ##########################################




############################# Search #############################################################
@login_required
def master_search(request):
    query = request.GET.get('q', '')

    tasks = Task.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
    appointments = Appointment.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(location__icontains=query))
    customers = Customer.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))
    leads = Lead.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(email__icontains=query))

    return render(request, 'crm_home/search_results.html', {
        'query': query,
        'tasks': tasks,
        'appointments': appointments,
        'customers': customers,
        'leads': leads,
    })