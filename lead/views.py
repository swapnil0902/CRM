from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .models import Lead
from .forms import LeadForm

@login_required
def lead_list(request):
    staff = request.user.staff  # Assuming user is a Staff instance
    leads = Lead.objects.filter(staff=staff)
    return render(request, 'lead_list.html', {'leads': leads})

@login_required
def lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    if lead.staff != request.user.staff:
        # Handle unauthorized access (e.g., raise PermissionDenied)
        return HttpResponseForbidden()
    return render(request, 'lead_detail.html', {'lead': lead})

def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            # Set other lead fields as needed, e.g., lead.staff = request.user.staff
            lead.save()
            return redirect('lead_list')
    else:
        form = LeadForm()

    return render(request, 'lead/lead_create.html', {'form': form})

def lead(request):
    return render(request, "lead/lead.html")
