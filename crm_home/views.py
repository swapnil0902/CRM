from .models import Company
from account.views import *
from task.models import Task
from lead.models import Lead
from django.db.models import Q
from django.utils import timezone
from customer.models import Customer
from django.core.mail import send_mail
from django.utils.html import strip_tags
from account.models import CompanyRequest
from appointment.models import Appointment
from django.template.loader import render_to_string
from django.contrib.auth.forms import UserChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import CompanyForm,AccountManagerForm,CompanyForm,UserUpdateForm



# Create your views here.
########################### Default Home Page ############################################
def home(request):
    return render(request,"crm_home/index.html")


############################  Dashboard View #############################################
@login_required
@user_passes_test(is_User_or_Manager)
def dashboard(request):
    future_tasks = Task.objects.filter(due_date__gte=timezone.now(), assigned_to=request.user)
    future_appointments = Appointment.objects.filter(start_date__gte=timezone.now(), attendees=request.user)

    context = {
        'future_tasks': future_tasks,
        'future_appointments': future_appointments,
    }
    return render(request, 'crm/dashboard.html', context)


########################### User Profile Page ############################################
@login_required
@user_passes_test(is_User_or_Manager)
def my_profile(request):
    return render(request,"crm_home/my_profile.html")


########################## Updating User Profile ##########################################
@login_required
@user_passes_test(is_User_or_Manager)
def update_user_profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_page')  
    else:
        form = UserUpdateForm(instance=request.user)
    
    return render(request, 'crm_home/update_profile.html', {'form': form})


############################ Creating Company ##############################################
@login_required
@user_passes_test(is_Admin)
def create_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('company_list') 
    else:
        form = CompanyForm()

    return render(request, 'crm_home/create_company.html', {'form': form})


############################ Creating Company(Admin) #######################################
@login_required
@user_passes_test(is_Admin)
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


############################# Company Lists ################################################
@login_required
@user_passes_test(is_Admin)
def company_list(request):
    companies = Company.objects.all()
    return render(request, 'crm_home/company_list.html', {'companies': companies})


############################ Company Details ###############################################
@login_required
@user_passes_test(is_Admin)
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


############################# Search #############################################################
@login_required
@user_passes_test(is_User_or_Manager)
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

############################## THE-END #############################################################