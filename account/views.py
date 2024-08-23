from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group
from .forms import GroupForm
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, update_session_auth_hash
from .forms import ActivatePasswordForm
from django.contrib.auth.models import User
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.core.mail import send_mail  # For sending the generated password
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from .models import UserRequest,CompanyRequest
from crm_home.models import Company
from .forms import UserRequestForm




def mngr_dashboard(request): #################################
    staffs = User.objects.filter(groups__name='Staff')
    account_managers = User.objects.filter(groups__name='Account Manager')
    
    context = {
        'staffs': staffs,
        'account_managers': account_managers,
    }
    return render(request, 'account/mngr_dashboard.html', context)

@login_required
def home(request):
    return render(request, 'crm/dashboard.html')

 

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'account/group_list.html', {'groups': groups})


def group_create(request):
    print("insider")
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            print("something")
            return redirect('mngr_dashboard')
        else:
            print("Form errors:", form.errors)
    else:
        form = GroupForm()
    return render(request, 'account/group_form.html', {'form': form})




# def group_update(request, pk):
#     group = get_object_or_404(Group, pk=pk)
#     if request.method == 'POST':
#         form = GroupForm(request.POST, instance=group)
#         if form.is_valid():
#             form.save()
#             return redirect("group_list")
#     else:
#         form = GroupForm(instance=group)
#     return render(request, 'account/group_form.html', {'form': form})

def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group_list')  # Redirect to the list of groups or another success page
    else:
        form = GroupForm(instance=group)
    
    return render(request, 'account/update_group.html', {'form': form})

def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('mngr_dashboard')
    return render(request, 'account/group_confirm_delete.html', {'group': group})


def signup(request, request_id=None):
    if request_id:
        user_request = get_object_or_404(UserRequest, id=request_id)  # Fetch the user request

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            username = form.cleaned_data.get('username')
            user = authenticate(username=username, password=password)
            login(request, user)

            # Create the HTML email content
            html_message = render_to_string(
                'account/email_template.html',  # HTML template for the email
                {
                    'first_name': user.first_name,
                    'username': username,
                    'password': password,
                    'support_email': 'sivatejat509@gmail.com',  # Replace with your support email
                    'login_url': 'http://localhost:8000/login/',  # Replace with your login URL
                }
            )
            plain_message = strip_tags(html_message)
            print(user.company)
            # Send the email
            send_mail(
                'Your Account Details and Instructions',
                plain_message,
                'sivatejat509@gmail.com',  # Your sender email
                [user.email],
                fail_silently=False,
                html_message=html_message,  # Send the HTML version
            )
            if user_request:
                user_request.delete()

            return redirect('home')
    else:
        # Pre-fill the signup form with user request data
        initial_data = {
            'first_name': user_request.first_name,
            'last_name': user_request.last_name,
            'email': user_request.email,
            # 'username': user_request.username,  # Assuming you have a username field in your request model
        }
        form = SignUpForm(initial=initial_data)

    return render(request, 'account/signup.html', {'form': form})


def manual_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user, password = form.save()
            username = form.cleaned_data.get('username')
            user = authenticate(username=username, password=password)
            login(request, user)

            # Create the HTML email content
            html_message = render_to_string(
                'account/email_template.html',  # HTML template for the email
                {
                    'first_name': user.first_name,
                    'username': username,
                    'password': password,
                    'support_email': 'sivatejat509@gmail.com',  # Replace with your support email
                    'login_url': 'http://localhost:8000/login/',  # Replace with your login URL
                }
            )
            plain_message = strip_tags(html_message)

            # Send the email
            send_mail(
                'Your Account Details and Instructions',
                plain_message,
                'sivatejat509@gmail.com',  # Your sender email
                [user.email],
                fail_silently=False,
                html_message=html_message,  # Send the HTML version
            )

            return redirect('home')
    else:
        # Create an empty form instance
        form = SignUpForm()

    return render(request, 'account/signup.html', {'form': form})



# def user_request_view(request):
#     if request.method == 'POST':
#         form = userRequestForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('request_submitted')  # Redirect to a thank you page or similar
#     else:
#         form = userRequestForm()
#     return render(request, 'account/user_request_form.html', {'form': form})


def user_request_view(request):
    # Retrieve the list of all companies
    companies = Company.objects.all()

    if request.method == 'POST':
        form = UserRequestForm(request.POST)
        if form.is_valid():
            # Save the form instance and print the company value for debugging
            form.save()
            print("Form Data:", form.cleaned_data)
            return redirect('request_submitted')  # Redirect to a thank you page or similar
    else:
        form = UserRequestForm()

    return render(request, 'account/user_request_form.html', {
        'form': form # Pass the list of companies to the template
    })

def company_request_view(request):
    if request.method == 'POST':
        form = UserRequestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('request_submitted')  # Redirect to a thank you page
    else:
        form = UserRequestForm()
    return render(request, 'account/company_request_form.html', {'form': form})

def list_new_company_requests(request):
    requests = CompanyRequest.objects.all()
    return render(request, 'account/list_new_company_requests.html', {'requests': requests})

def request_submitted_view(request):
    return render(request, 'account/request_submitted.html')

def user_requests_view(request):
    # Fetch all user requests from the database
    user_requests = UserRequest.objects.all()
    
    # Render the template with the user requests
    return render(request, 'account/user_requests.html', {'user_requests': user_requests})


# @login_required
def activate_password(request):
    users = User.objects.all()
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Date Joined: {user.date_joined}")
        
        if user == authenticate(request, password=user.password):
            print(f"Password matches for user: {user.username}")
        else:
            print(f"Password does not match for user: {user.username}")
        print("-" * 40) # Separator for clarity

    if request.method == 'POST':
        form = ActivatePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password1 = form.cleaned_data['new_password1']

            # Check if the old password is correct
            if not request.user.check_password(old_password):
                print(old_password)
                print(new_password1)
                form.add_error('old_password', 'The old password is incorrect.')
            else:
                # Set the new password
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keeps the user logged in after password change
                return redirect('home')
    else:
        form = ActivatePasswordForm()

    return render(request, 'account/activate_password.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect("/")