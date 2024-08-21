from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import Group
from .forms import GroupForm


# @login_required
def home(request):
    return render(request, 'account/home.html')

 

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'account/group_list.html', {'groups': groups})

def group_create(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            return redirect('group_list')
    else:
        form = GroupForm()
    return render(request, 'account/group_form.html', {'form': form})

def group_update(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect("group_list")
    else:
        form = GroupForm(instance=group)
    return render(request, 'account/group_form.html', {'form': form})

def group_delete(request, pk):
    group = get_object_or_404(Group, pk=pk)
    if request.method == 'POST':
        group.delete()
        return redirect('group_list')
    return render(request, 'account/group_confirm_delete.html', {'group': group})


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import SignUpForm
from django.contrib.auth import login, authenticate

from django.core.mail import send_mail  # For sending the generated password

from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string

def signup(request):
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
                    'support_email': 'support@yourdomain.com',  # Replace with your support email
                    'login_url': 'https://yourdomain.com/login',  # Replace with your login URL
                    'activation_url':'http://localhost:8000/activate'
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
        form = SignUpForm()
    return render(request, 'account/signup.html', {'form': form})


from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, update_session_auth_hash
from .forms import ActivatePasswordForm

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