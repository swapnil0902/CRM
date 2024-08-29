from .models import Lead
from account.views import *
from .forms import LeadForm
from django.http import Http404
from rest_framework import viewsets
from .serializers import LeadSerializer
from django.http import HttpResponseNotAllowed
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from crm_home.models import Company, UserProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect


######################## Import The User Data ##########################################
User = get_user_model()


####################### Leads Creation Using Viewsets ##################################
class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


############################ Lead Lists ################################################
@login_required
@user_passes_test(is_User_or_Manager)
def lead_list(request):
    user = request.user 
    leads = Lead.objects.filter(staff=request.user )
    return render(request, 'lead/lead.html', {'leads': leads})


############################# Lead Details(Individual) ##################################
@login_required
@api_view(['POST', 'GET'])
@user_passes_test(is_User)
def lead_detail(request, lead_id):
    try:
        lead = get_object_or_404(Lead, id=lead_id)
    except Http404:
        return redirect('lead-view') 
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead, user = request.user)
        if form.is_valid():
            form.save()
            return redirect('lead_detail', lead_id=lead_id)
        else:
            return render(request, 'lead/lead_detail.html', {'lead': lead, 'form': form})
    
    elif request.method == 'GET':
        form = LeadForm(instance=lead, user = request.user, initial={'staff': request.user})
        return render(request, 'lead/lead_detail.html', {'lead': lead, 'form': form})
    
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    

############################ Creating Leads ###########################################
@login_required
@user_passes_test(is_User_or_Manager)
def lead_create(request):
    if request.method == 'POST':
        form = LeadForm(request.POST, user=request.user)
        if form.is_valid():
            lead = form.save(commit=False)

            if request.user.groups.filter(name='Staff').exists(): 
                lead.staff = request.user
                lead.company = request.user.userprofile.company
            elif request.user.groups.filter(name='Account Manager').exists():  
                lead.company = request.user.userprofile.company
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


############################ Deleting Leads ###########################################
@api_view(['GET', 'DELETE'])
@user_passes_test(is_User_or_Manager)
def lead_delete(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    lead.delete()
    return redirect('lead-view')


######################## Lead Lists(Company-Wise) ######################################
@login_required
@user_passes_test(is_Account_Manager)
def company_lead_list(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    company = request.user.userprofile.company

    leads = Lead.objects.filter(company=company)

    return render(request, 'lead/company_lead_list.html', {'leads': leads})


######################## Lead Lists Details(Individual-Company-Wise) ###################
@api_view(['POST', 'GET'])
@user_passes_test(is_User_or_Manager)
def company_lead_detail(request, lead_id):
    try:
        lead = get_object_or_404(Lead, id=lead_id)
    except Http404:
        return redirect('company_lead_list') 
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead, user = request.user)
        if form.is_valid():
            form.save()
            return redirect('company_lead_detail', lead_id=lead_id)
        else:
            return render(request, 'lead/company_lead_detail.html', {'lead': lead, 'form': form})
    
    elif request.method == 'GET':
        form = LeadForm(instance=lead, user = request.user, initial={'staff': request.user})
        return render(request, 'lead/company_lead_detail.html', {'lead': lead, 'form': form})
    
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    

######################## Deleting Leads(Company) ##########################################
@api_view(['GET', 'DELETE'])
@user_passes_test(is_Account_Manager)
def company_lead_delete(request, lead_id):
    lead = get_object_or_404(Lead, id=lead_id)

    lead.delete()
    return redirect('company_lead_list')

################################# THE-END #################################################