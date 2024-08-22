from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            if request.user.groups.filter(name='Staff').exists():
                appointment.save()  # Save the appointment first before setting many-to-many relationships
                appointment.attendees.set([request.user])  # Assign the current user to the attendees
            else:
                appointment.save()
            form.save_m2m()  # Save many-to-many relationships like attendees
            return redirect('appointment_list')
    else:
        form = AppointmentForm(user=request.user)
    return render(request, 'appointment/appointment_form.html', {'form': form})

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

@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointment/appointment_confirm_delete.html', {'appointment': appointment})

@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(attendees=request.user)
    return render(request, 'appointment/appointment_list.html', {'appointments': appointments})
