from django.views import View
from django.contrib import messages
from django.core.mail import send_mail
from django.utils.html import strip_tags
from .models import UserRequest, CompanyRequest
from crm_home.models import Company, UserProfile
from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import GroupForm, SignUpForm, UserRequestForm, CompanyRequestForm
from django.contrib.auth import logout, update_session_auth_hash, authenticate, login as auth_login


# @login_required
# def check_session(request):
#     if request.user.is_authenticated:
#         # Session is active
#         return JsonResponse({'active': True})
#     else:
#         # Session has expired
#         return JsonResponse({'active': False})
    





def is_Account_Manager(user):
    return user.groups.filter(name='Owner').exists()
def is_User(user):
    return user.groups.filter(name='chef').exists()
def is_User_or_Manager(user):
    return is_User(user) or is_Account_Manager(user)


# class CustomLoginView(View):
#     form_class = AuthenticationForm  # You can use CustomAuthenticationForm if you created it
#     template_name = 'registration/login.html'  # Default template name used by built-in login view

#     def get(self, request):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})

#     def post(self, request):
#         form = self.form_class(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             auth_login(request, user)
#             if user.is_superuser:
#                 next_url = '/companies/'
#             elif user.groups.filter(name='Account Manager').exists():
#                 next_url = '/dash/'
#             elif user.groups.filter(name='Staff').exists():
#                 next_url = '/dash/'
#             else:
#                 next_url = '/'

#             return redirect(next_url)
#         else:
#             messages.error(request, 'Invalid username or password.')
        
#         return render(request, self.template_name, {'form': form})

from django.core.mail import send_mail
import random
from django.conf import settings

class CustomLoginView(View):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    otp_template_name = 'registration/otp.html'  # Template for OTP verification

    def get(self, request):
        if 'otp_verified' in request.session and request.session['otp_verified']:
            # OTP already verified, proceed with login
            return self._redirect_user(request.user)

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if 'otp_sent' in request.session and request.session['otp_sent']:
            # OTP was sent, now verify OTP
            otp = request.POST.get('otp')
            if otp and otp == request.session.get('otp'):
                # OTP is correct
                user = authenticate(username=request.session['username'], password=request.session['password'])
                if user:
                    auth_login(request, user)
                    request.session['otp_verified'] = True
                    return self._redirect_user(user)
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.otp_template_name)

        # Regular login flow
        form = self.form_class(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            request.session['username'] = form.cleaned_data.get('username')
            request.session['password'] = form.cleaned_data.get('password')
            otp = self.generate_otp()
            request.session['otp'] = otp
            request.session['otp_sent'] = True
            self.send_otp_via_email(user.email, otp)
            messages.info(request, 'An OTP has been sent to your email. Please enter it to continue.')
            return render(request, self.otp_template_name)
        else:
            messages.error(request, 'Invalid username or password.')

        return render(request, self.template_name, {'form': form})

    def _redirect_user(self, user):
        """Redirects user based on their group."""
        if user.is_superuser:
            next_url = '/companies/'
        elif user.groups.filter(name='Account Manager').exists():
            next_url = '/dash/'
        elif user.groups.filter(name='Staff').exists():
            next_url = '/dash/'
        else:
            next_url = '/'
        return redirect(next_url)

    def generate_otp(self):
        """Generates a 6-digit OTP."""
        return str(random.randint(100000, 999999))

    def send_otp_via_email(self, email, otp):
        """Sends OTP to the given email."""
        subject = 'Your OTP Code'
        message = f'Your OTP code is {otp}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)





@login_required
# @user_passes_test(is_Account_Manager)
def mngr_dashboard(request):
    user_profile = request.user.userprofile
    company_users = User.objects.filter(userprofile__company=user_profile.company)
    staffs = company_users.filter(groups__name='Staff')
    account_managers = company_users.filter(groups__name='Account Manager')
    
    context = {
        'staffs': staffs,
        'account_managers': account_managers,
    }
    print(account_managers)
    return render(request, 'account/mngr_dashboard.html', context)

@login_required
# @user_passes_test(is_User_or_Manager)
def home(request):
    return render(request, 'crm/dashboard.html')

 
@login_required
# @user_passes_test(is_User_or_Manager)
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'account/group_list.html', {'groups': groups})

@login_required
def group_create(request):
    print("insider")
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            print("something")
            return redirect('group_list')
        else:
            print("Form errors:", form.errors)
    else:
        form = GroupForm()
    return render(request, 'account/group_form.html', {'form': form})


@login_required
def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')  
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'account/update_group.html', {'form': form})
@login_required
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'account/group_confirm_delete.html', {'group': group})

@login_required
def signup(request, request_id=None):
    if request_id:
        user_request = get_object_or_404(UserRequest, id=request_id)  # Fetch the user request

    account_manager_profile = UserProfile.objects.get(staff=request.user)
    company = account_manager_profile.company

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            username = form.cleaned_data.get('username')

            UserProfile.objects.create(
                staff=user,
                company=company
            )
            print('created')
            
            html_message = render_to_string(
                'account/email_template.html',  
                {
                    'first_name': user.first_name,
                    'username': username,
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
                [user.email],
                fail_silently=False,
                html_message=html_message,  
            )
            if user_request:
                user_request.delete()

            return redirect('home')
    else:
         
        initial_data = {
            'first_name': user_request.first_name,
            'last_name': user_request.last_name,
            'email': user_request.email,
            
        }
        form = SignUpForm(initial=initial_data)

    return render(request, 'account/signup.html', {'form': form})

@login_required
def manual_signup(request):
    account_manager_profile = UserProfile.objects.get(staff=request.user)
    company = account_manager_profile.company

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            UserProfile.objects.create(
                staff=user,
                company=company
            )
            username = form.cleaned_data.get('username')
            
 
            html_message = render_to_string(
                'account/email_template.html',  
                {
                    'first_name': user.first_name,
                    'username': username,
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
                [user.email],
                fail_silently=False,
                html_message=html_message,   
            )

            return redirect('home')
    else:
        form = SignUpForm()

    return render(request, 'account/signup.html', {'form': form})



def user_request_view(request):
    companies = Company.objects.all()

    if request.method == 'POST':
        form = UserRequestForm(request.POST)
        if form.is_valid():
            form.save()
            print("Form Data:", form.cleaned_data)
            return redirect('request_submitted') 
    else:
        form = UserRequestForm()

    return render(request, 'account/user_request_form.html', {
        'form': form  
    })

def company_request_view(request):
    if request.method == 'POST':
        form = CompanyRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('request_submitted')  
    else:
        form = CompanyRequestForm()
    return render(request, 'account/company_request_form.html', {'form': form})
@login_required
def list_new_company_requests(request):
    requests = CompanyRequest.objects.all()
    return render(request, 'account/list_new_company_requests.html', {'requests': requests})

def request_submitted_view(request):
    return render(request, 'account/request_submitted.html')
@login_required
def user_requests_view(request): 
    user_profile = request.user.userprofile
 
    user_requests = UserRequest.objects.filter(company=user_profile.company)
     
    return render(request, 'account/user_requests.html', {'user_requests': user_requests})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/")