from django.contrib.auth.models import Group

def user_groups(request):
    user = request.user
    return {
        'is_admin': user.is_authenticated and user.is_superuser,
        'is_accMngr': user.is_authenticated and user.groups.filter(name='Account Manager').exists(),
        'is_staff': user.is_authenticated and user.groups.filter(name='Staff').exists(),
    }
