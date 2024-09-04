from crm_home.models import UserProfile
from .models import AuditLogDetails
from django.utils import timezone

def get_user_details(request):
    user = request.user
    username = user.username
    try:
        user_profile = UserProfile.objects.get(staff=user)
        user_company = user_profile.company.name
    except UserProfile.DoesNotExist:
        user_company = 'Unknown'

    group_names = ', '.join(group.name for group in user.groups.all()) or 'No Group'

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0] 
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    return {
        'username': username,
        'user_company': user_company,
        'group_names': group_names,
        'ip_address': ip_address,
    }


def create_audit_log(username, user_company=None, group=None, ip_address=None,description=None):

    AuditLogDetails.objects.create(
        user_name=username,
        user_company=user_company,
        group=group,
        ip_address=ip_address,
        timestamp=timezone.now(),
        description=description
    )