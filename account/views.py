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


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from .forms import UsernamePasswordResetForm, OTPForm, SetNewPasswordForm  # Ensure these forms are defined
from django.http import HttpResponse



import random
from django.utils import timezone
from datetime import timedelta

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
                otp = str(random.randint(100000, 999999))  # Generate a random OTP
                otp_generated_at = timezone.now()  # Store the current time
                
                message = render_to_string('registration/password_reset_email.html', {
                    'user': user,
                    'domain': current_site.domain,
                    'uid': uid,
                    'token': token,
                    'otp': otp,
                })
                send_mail(subject, message, None, [user.email])
                
                # Store data in session
                request.session['reset_username'] = username
                request.session['otp'] = otp
                request.session['otp_generated_at'] = otp_generated_at.isoformat()  # Store as ISO 8601 string
                
                return redirect('verify_otp')
            except User.DoesNotExist:
                form.add_error('username', 'User with this username does not exist.')
    else:
        form = UsernamePasswordResetForm()
    
    return render(request, 'registration/forgot_password.html', {'form': form})


from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from datetime import datetime, timedelta

# def verify_otp(request):
#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid():
#             entered_otp = form.cleaned_data['otp']
#             stored_otp = request.session.get('otp')
#             otp_generated_at = request.session.get('otp_generated_at')
            
#             if not otp_generated_at:
#                 form.add_error(None, 'OTP expired or not found.')
#             else:
#                 # Parse ISO 8601 string using datetime
#                 otp_generated_at = datetime.fromisoformat(otp_generated_at)
#                 now = timezone.now()  # Get current time
                
#                 if now - otp_generated_at > timedelta(minutes=1):
#                     form.add_error(None, 'OTP has expired. Please request a new one.')
#                 elif entered_otp == stored_otp:
#                     return redirect('password_reset_confirm')
#                 else:
#                     form.add_error('otp', 'Invalid OTP. Please try again.')
#     else:
#         form = OTPForm()

#     return render(request, 'registration/verify_otp.html', {'form': form})
from django.utils import timezone
from datetime import datetime, timedelta

# def verify_otp(request):
#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid():
#             entered_otp = form.cleaned_data['otp']
#             stored_otp = request.session.get('otp')
#             otp_generated_at = request.session.get('otp_generated_at')
            
#             if not otp_generated_at:
#                 form.add_error(None, 'OTP expired or not found.')
#             else:
#                 otp_generated_at = datetime.fromisoformat(otp_generated_at)
#                 now = timezone.now()  # Get current time
                
#                 if now - otp_generated_at > timedelta(minutes=1):
#                     form.add_error(None, 'OTP has expired. Please request a new one.')
#                 elif entered_otp == stored_otp:
#                     return redirect('password_reset_confirm')
#                 else:
#                     form.add_error('otp', 'Invalid OTP. Please try again.')
#     else:
#         form = OTPForm()
#         otp_generated_at = request.session.get('otp_generated_at')
#         if otp_generated_at:
#             otp_generated_at = datetime.fromisoformat(otp_generated_at)
#             now = timezone.now()
#             remaining_time = max(0, 60 - (now - otp_generated_at).total_seconds())
#         else:
#             remaining_time = 0
    
#     return render(request, 'registration/verify_otp.html', {'form': form, 'remaining_time': remaining_time})


from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib import messages
from .forms import OTPForm

def verify_otp(request):
    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            stored_otp = request.session.get('otp')
            otp_generated_at = request.session.get('otp_generated_at')

            if not otp_generated_at:
                # Redirect to 'forgot password' page if OTP is not found
                return redirect('forgot_password')

            otp_generated_at = datetime.fromisoformat(otp_generated_at)
            now = timezone.now()  # Get current time

            # Check if the OTP has expired
            if now - otp_generated_at > timedelta(minutes=1):
                # Redirect to 'forgot password' page if OTP has expired
                return redirect('forgot_password')
            elif entered_otp == stored_otp:
                # Redirect to password reset confirmation if OTP is correct
                return redirect('password_reset_confirm')
            else:
                # Add an error if the OTP is invalid
                form.add_error('otp', 'Invalid OTP. Please try again.')
    else:
        form = OTPForm()
        otp_generated_at = request.session.get('otp_generated_at')
        if otp_generated_at:
            otp_generated_at = datetime.fromisoformat(otp_generated_at)
            now = timezone.now()
            
            # Calculate the remaining time for OTP expiration
            remaining_time = max(0, 60 - (now - otp_generated_at).total_seconds())
            
            # Check if OTP has already expired
            if remaining_time == 0:
                # Redirect to 'forgot password' page if OTP has expired
                return redirect('forgot_password')
        else:
            remaining_time = 0

    return render(request, 'registration/verify_otp.html', {'form': form, 'remaining_time': remaining_time})




def password_reset_confirm(request):
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            username = request.session.get('reset_username')
            new_password = form.cleaned_data['new_password']
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



# def forgot_password(request):
#     if request.method == 'POST':
#         form = UsernamePasswordResetForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data['username']
#             try:
#                 user = User.objects.get(username=username)
#                 token = default_token_generator.make_token(user)
#                 uid = urlsafe_base64_encode(force_bytes(user.pk))
#                 current_site = get_current_site(request)
#                 subject = 'Password Reset Requested'
#                 # otp = "123456"  # You should generate a random OTP and store it securely
#                 otp = str(random.randint(100000, 999999)) 
#                 message = render_to_string('registration/password_reset_email.html', {
#                     'user': user,
#                     'domain': current_site.domain,
#                     'uid': uid,
#                     'token': token,
#                     'otp': otp,
#                 })
#                 send_mail(subject, message, None, [user.email])
#                 request.session['reset_username'] = username  # Storing username for OTP verification
#                 request.session['otp'] = otp  # Storing OTP for later verification
#                 return redirect('verify_otp')  # Redirect to OTP verification page
#             except User.DoesNotExist:
#                 form.add_error('username', 'User with this username does not exist.')
#     else:
#         form = UsernamePasswordResetForm()
    
#     return render(request, 'registration/forgot_password.html', {'form': form})


# def verify_otp(request):
#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid():
#             entered_otp = form.cleaned_data['otp']
#             stored_otp = request.session.get('otp')
#             if entered_otp == stored_otp:
#                 return redirect('password_reset_confirm')
#             else:
#                 form.add_error('otp', 'Invalid OTP. Please try again.')
#     else:
#         form = OTPForm()

#     return render(request, 'registration/verify_otp.html', {'form': form})


# def password_reset_confirm(request):
#     if request.method == 'POST':
#         form = SetNewPasswordForm(request.POST)
#         if form.is_valid():
#             username = request.session.get('reset_username')
#             new_password = form.cleaned_data['new_password']
#             try:
#                 user = User.objects.get(username=username)
#                 user.set_password(new_password)
#                 user.save()
#                 messages.success(request, 'Password reset successfully.')
#                 return redirect('login')
#             except User.DoesNotExist:
#                 form.add_error(None, 'Error resetting password. Please try again.')
#     else:
#         form = SetNewPasswordForm()

#     return render(request, 'registration/password_reset_form.html', {'form': form})
