import random
from .serializers import *
from django.views import View
from datetime import timedelta
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.utils.html import strip_tags
from django.utils.encoding import force_bytes
from .models import UserRequest, CompanyRequest
from rest_framework.viewsets import ModelViewSet
from crm_home.models import Company, UserProfile
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import logout,authenticate, login as auth_login
from .forms import UsernamePasswordResetForm, OTPForm, SetNewPasswordForm
from django.contrib.auth.decorators import login_required,user_passes_test
from .forms import GroupForm, SignUpForm, UserRequestForm, CompanyRequestForm



@login_required
def check_session(request):
    return JsonResponse({'status': 'ok'})

############################### API ##############################################

class UserRequestList(ModelViewSet):
    queryset = UserRequest.objects.all()
    serializer_class = UserRequestListSerializer
    permission_classes = (IsAuthenticated,IsAdminUser)


class UserList(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,IsAdminUser)


class CompanyRequestList(ModelViewSet):
    queryset = CompanyRequest.objects.all()
    serializer_class = CompanyRequestListSerializer
    permission_classes = (IsAuthenticated,IsAdminUser)


############################# Dividing Groups #########################################################
def is_Account_Manager(user):
    return user.groups.filter(name='Account Manager').exists()
def is_User(user):
    return user.groups.filter(name='Staff').exists()
def is_User_or_Manager(user):
    return is_User(user) or is_Account_Manager(user)
def is_Admin(user):
    return user.is_superuser


############################# Build-In Django View ######################################################
class CustomLoginView(View):
    form_class = AuthenticationForm
    template_name = 'registration/login.html'
    otp_template_name = 'registration/otp.html' 

    def get(self, request):
        if 'otp_verified' in request.session and request.session['otp_verified']:
            return self._redirect_user(request.user)

        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        if 'otp_sent' in request.session and request.session['otp_sent']:
            otp = request.POST.get('otp')
            if otp and otp == request.session.get('otp'):
                user = authenticate(username=request.session['username'], password=request.session['password'])
                if user:
                    auth_login(request, user)
                    request.session['otp_verified'] = True
                    return self._redirect_user(user)
            messages.error(request, 'Invalid OTP. Please try again.')
            return render(request, self.otp_template_name)

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


############################# Manager Dashboard ######################################################
@login_required
@user_passes_test(is_Account_Manager)
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


############################### Home Page ############################################################
@login_required
def home(request):
    return render(request, 'crm/dashboard.html')


############################# Dividing Groups #########################################################
@login_required
@user_passes_test(is_Account_Manager)
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'account/group_list.html', {'groups': groups})

@login_required
@user_passes_test(is_Admin)
def group_list_Admin(request):
    groups = Group.objects.all()
    return render(request, 'account/group_list_Admin.html', {'groups': groups})

############################# Creating Groups #########################################################
@login_required
@user_passes_test(is_Account_Manager)
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
@user_passes_test(is_Admin)
def group_create_Admin(request):
    print("insider")
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            print("something")
            return redirect('group_list_Admin')
        else:
            print("Form errors:", form.errors)
    else:
        form = GroupForm()
    return render(request, 'account/group_form_Admin.html', {'form': form})

############################# Updating Groups #########################################################
@login_required
@user_passes_test(is_Account_Manager)
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
@user_passes_test(is_Admin)
def group_update_Admin(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list_Admin')  
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'account/update_group_Admin.html', {'form': form})

############################# Deleting Groups #########################################################
@login_required
@user_passes_test(is_Account_Manager)
def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'account/group_confirm_delete.html', {'group': group})

@login_required
@user_passes_test(is_Admin)
def group_delete_Admin(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list_Admin')
    return render(request, 'account/group_confirm_delete_Admin.html', {'group': group})
################################ Sign-Up Page ##########################################################
@login_required
@user_passes_test(is_Account_Manager)
def signup(request, request_id=None):
    user_request = None
    if request_id:
        user_request = get_object_or_404(UserRequest, id=request_id)   

    account_manager_profile = UserProfile.objects.get(staff=request.user)
    company = account_manager_profile.company

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        email = form.data.get('email')
    
        if User.objects.filter(email=email).exists():
            form.add_error('email', 'A user with this email already exists.')
        elif form.is_valid():
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

            return redirect('mngr_dashboard')
    else:
        initial_data = {
            'first_name': user_request.first_name if user_request else '',
            'last_name': user_request.last_name if user_request else '',
            'email': user_request.email if user_request else '',
        }
        form = SignUpForm(initial=initial_data)

    return render(request, 'account/signup.html', {'form': form})


############################# Adding User Manually ######################################################
@login_required
@user_passes_test(is_Account_Manager)
def manual_signup(request):
    account_manager_profile = UserProfile.objects.get(staff=request.user)
    company = account_manager_profile.company

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        email = form.data.get('email')
 
        if User.objects.filter(email=email).exists():
            form.add_error('email', 'A user with this email already exists.')
        elif form.is_valid():
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

            return redirect('mngr_dashboard')
    else:
        form = SignUpForm()

    return render(request, 'account/signup.html', {'form': form})

############################# User Lists #########################################################
def user_request_view(request):
    companies = Company.objects.all()

    if request.method == 'POST':
        form = UserRequestForm(request.POST)
        email = form.data.get('email')  

        if User.objects.filter(email=email).exists():
            form.add_error('email', 'A user with this email already exists.')
        elif form.is_valid():
            form.save()
            print("Form Data:", form.cleaned_data)
            return redirect('request_submitted') 
    else:
        form = UserRequestForm()

    return render(request, 'account/user_request_form.html', {
        'form': form  
    })


############################# Companies List ######################################################
def company_request_view(request):
    if request.method == 'POST':
        form = CompanyRequestForm(request.POST)
        company_name = form.data.get('name') 
        
        if Company.objects.filter(name=company_name).exists():
            form.add_error('name', 'A company with this name already exists.')
        elif form.is_valid():
            form.save()
            return redirect('request_submitted')  
    else:
        form = CompanyRequestForm()

    return render(request, 'account/company_request_form.html', {'form': form})


############################# Adding New Company Manually ##########################################
@login_required
@user_passes_test(is_Admin)
def list_new_company_requests(request):
    requests = CompanyRequest.objects.all()
    return render(request, 'account/list_new_company_requests.html', {'requests': requests})


############################# Requested Company #########################################################
def request_submitted_view(request):
    return render(request, 'account/request_submitted.html')


############################# User Profile Lists(Company Wise) ###########################################
@login_required
@user_passes_test(is_Account_Manager)
def user_requests_view(request): 
    user_profile = request.user.userprofile
    user_requests = UserRequest.objects.filter(company=user_profile.company)
    return render(request, 'account/user_requests.html', {'user_requests': user_requests})


@login_required
@user_passes_test(is_Account_Manager)
def delete_user_request(request, request_id):
    user_request = get_object_or_404(UserRequest, id=request_id)
    if request.method == 'POST':
        user_request.delete()
        messages.success(request, 'User request has been deleted successfully.')
        return redirect('user_requests')
    return render(request, 'account/user_requests.html')

################################## Logout View ############################################################
@login_required
def logout_view(request):
    logout(request)
    return redirect("/")


################################## Forgot Password #########################################################
def forgot_password(request):
    if request.method == 'POST':
        form = UsernamePasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                current_site = get_current_site(request)
                subject = 'Password Reset Requested'
                otp = str(random.randint(100000, 999999))  
                otp_generated_at = timezone.now() 
                
                message = render_to_string('registration/password_reset_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                    'otp': otp,
                })
                send_mail(subject, message, None, [user.email])
                
                request.session['reset_username'] = username
                request.session['otp'] = otp
                request.session['otp_generated_at'] = otp_generated_at.isoformat() 
                
                return redirect('verify_otp')
            except User.DoesNotExist:
                form.add_error('username', 'User with this username does not exist.')
    else:
        form = UsernamePasswordResetForm()
    
    return render(request, 'registration/forgot_password.html', {'form': form})


################################## OTP Validation #######################################################
def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.session.get('otp')
            otp_generated_at = request.session.get('otp_generated_at')

            if not otp_generated_at:
                return redirect('forgot_password')

            otp_generated_at = datetime.fromisoformat(otp_generated_at)
            now = timezone.now() 

            if now - otp_generated_at > timedelta(minutes=1):
                return redirect('forgot_password')
            elif entered_otp == stored_otp:
                return redirect('password_reset_confirm')
            else:
                form.add_error('otp', 'Invalid OTP. Please try again.')
    else:
        form = OTPForm()
        otp_generated_at = request.session.get('otp_generated_at')
        if otp_generated_at:
            otp_generated_at = datetime.fromisoformat(otp_generated_at)
            now = timezone.now()
            remaining_time = max(0, 60 - (now - otp_generated_at).total_seconds())
            if remaining_time == 0:
                return redirect('forgot_password')
        else:
            remaining_time = 0
    return render(request, 'registration/verify_otp.html', {'form': form, 'remaining_time': remaining_time})


################################## Reset Password #########################################################
def password_reset_confirm(request):
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            username = request.session.get('reset_username')
            new_password = form.cleaned_data['new_password']
            try:
                validate_password(new_password)
            except ValidationError as e:
                form.add_error('new_password', e)
            else:
                try:
                    user = User.objects.get(username=username)
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password reset successfully.')
                    return redirect('login')
                except User.DoesNotExist:
                    form.add_error(None, 'Error resetting password. Please try again.')
    else:
        form = SetNewPasswordForm()
    return render(request, 'registration/password_reset_form.html', {'form': form})

################################## Delete Account #########################################################

def delete_account(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('home')
    return render(request, 'account/delete_account.html')


################################## Delete My User #########################################################

def delete_my_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('mngr_dashboard')  
    else:
        return redirect('mngr_dashboard')  
    

################################## THE-END #########################################################