from .models import Appointment
from .forms import AppointmentForm
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


############################# Creating an appointment #########################################################
@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
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
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointment/appointment_form.html', {'form': form})


############################# Deleting an appointment #########################################################
@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_confirm_delete.html', {'appointment': appointment})


############################# Appointments List #################################################################
@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(attendees=request.user)
    return render(request, 'appointment/appointment_list.html', {'appointments': appointments})


############################# Company Appointment List ##########################################################
@login_required
def company_appointment_list(request):
    company = request.user.userprofile.company
    appointments = Appointment.objects.filter(company=company)
    return render(request, 'appointment/company_appointment_list.html', {'appointments': appointments})


############################# Updating Company List #############################################################
@login_required
def company_appointment_update(request, pk):
    company = request.user.userprofile.company
    appointment = get_object_or_404(Appointment, pk=pk, company=company)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('company_appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointment/company_appointment_form.html', {'form': form})


############################# Deleting Company List #############################################################
@login_required
@api_view(['GET', 'DELETE'])
def company_appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    appointment.delete()
    return redirect('account/company_appointment_list')