from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.contrib.auth.decorators import login_required
from .models import Lead
from crm_home.models import Company, UserProfile
from .forms import LeadForm
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.decorators import api_view
from .serializers import LeadSerializer

User = get_user_model()


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


# @login_required
def lead_list(request):
    user = request.user 
    leads = Lead.objects.filter(staff=request.user )
    # leads = Lead.objects.all()
    return render(request, 'lead/lead.html', {'leads': leads})

# @login_required
@api_view(['POST', 'GET'])
def lead_detail(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)
    # if lead.staff != request.user:
    #     # Handle unauthorized access (e.g., raise PermissionDenied)
    #     return HttpResponseForbidden()
    # return render(request, 'lead/lead_detail.html', {'lead': lead})
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            return redirect('lead_detail', lead_id=lead_id)
        else:
            return render(request, 'lead/lead_detail.html', {'lead': lead, 'form': form})
    
    # elif request.method == 'DELETE':
    #     lead.delete()
    #     return redirect('lead-view')
    
    elif request.method == 'GET':
        form = LeadForm(instance=lead)
        return render(request, 'lead/lead_detail.html', {'lead': lead, 'form': form})
    
    else:
        return HttpResponseNotAllowed(['GET', 'POST', 'DELETE'])
    

@api_view(['GET', 'DELETE'])
def lead_delete(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    lead.delete()
    return redirect('lead-view')


    

def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, user=request.user)
        if form.is_valid():
            lead = form.save(commit=False)

            if request.user.groups.filter(name='Staff').exists(): 
                lead.staff = request.user
            elif request.user.groups.filter(name='Account Manager').exists(): 
                assigned_to_id = request.POST.get('staff')  
                if assigned_to_id:
                    lead.staff = get_object_or_404(User, pk=assigned_to_id)
                else:
                    form.add_error('staff', 'You must assign this lead to a staff member.')
                    return render(request, 'lead/lead_create.html', {'form': form, 'user': request.user})

            lead.save()
            return redirect('lead-view')
    else:
        form = LeadForm(user=request.user)
        if request.user.groups.filter(name='Account Manager').exists():
            company = get_object_or_404(Company, pk=request.user.userprofile.company.pk)
            form.fields['staff'].queryset = User.objects.filter(userprofile__company=company)

    return render(request, 'lead/lead_create.html', {'form': form, 'user': request.user})

# def lead(request):
#     return render(request, "lead/lead.html")
