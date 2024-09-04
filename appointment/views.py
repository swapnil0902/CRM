from account.utils import *
from account.views import *
from django.db.models import Q
from .models import Appointment
from .forms import AppointmentForm
from account.models import AuditLogDetails
from .serializers import AppointmentSerializer
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth.decorators import login_required,user_passes_test

############################### API ##############################################

class AppointmentList(ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = (IsAuthenticated,IsAdminUser)

############################# Creating an appointment #########################################################
@login_required
@user_passes_test(is_User_or_Manager)
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Appointment is created by {request.user}",
                ip_address=user_details['ip_address']
            )
            if request.user.groups.filter(name='Staff').exists():
                appointment.save()  
                appointment.attendees.set([request.user])  
            else:
                appointment.save()
            form.save_m2m()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)
    return render(request, 'appointment/appointment_form.html', {'form': form})


############################# Updating an appointment #########################################################
@login_required
@user_passes_test(is_User_or_Manager)
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, user=request.user)
        if form.is_valid():
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Appointment is Updated by {request.user}",
                ip_address=user_details['ip_address']
            )
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment, user=request.user)
    return render(request, 'appointment/appointment_form.html', {'form': form})


############################# Deleting an appointment #########################################################
@login_required
@user_passes_test(is_User_or_Manager)
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        user_details = get_user_details(request)
        create_audit_log(
            username=user_details['username'],
            user_company=user_details['user_company'],
            group=user_details['group_names'],
            description=f"Appointment is deleted by {request.user}",
            ip_address=user_details['ip_address']
        )
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_confirm_delete.html', {'appointment': appointment})


############################# Appointments List #################################################################
@login_required
@user_passes_test(is_User_or_Manager)
def appointment_list(request):
    query = request.GET.get('q', '')

    user_profile = UserProfile.objects.get(staff=request.user)
    company = user_profile.company

    appointments = Appointment.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query) | 
        Q(location__icontains=query),
        attendees=request.user,
        customer__company=company 
    ).distinct()

    return render(request, 'appointment/appointment_list.html', {'appointments': appointments, 'query': query})


############################# Company Appointment List ##########################################################
@login_required
@user_passes_test(is_Account_Manager)
def company_appointment_list(request):
    company = request.user.userprofile.company
    appointments = Appointment.objects.filter(attendees__userprofile__company=company).distinct()
    return render(request, 'appointment/company_appointment_list.html', {'appointments': appointments})


############################# Updating Company List #############################################################
@login_required
@user_passes_test(is_Account_Manager)
def company_appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment, user=request.user)
        if form.is_valid():
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Appointment is created by {request.user}",
                ip_address=user_details['ip_address']
            )
            form.save()
            return redirect('company_appointment_list')
    else:
        form = AppointmentForm(instance=appointment, user=request.user)
    return render(request, 'appointment/company_appointment_form.html', {'form': form})


############################# Deleting Company List #############################################################
@login_required
@user_passes_test(is_Account_Manager)
@api_view(['GET', 'DELETE'])
def company_appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user_details = get_user_details(request)
    create_audit_log(
        username=user_details['username'],
        user_company=user_details['user_company'],
        group=user_details['group_names'],
        description=f"Appointment is Deleted by {request.user}",
        ip_address=user_details['ip_address']
    )
    appointment.delete()
    return redirect('company_appointment_list')

#######################################    THE-END    #############################################################