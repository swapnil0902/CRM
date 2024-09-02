from .models import Lead
from account.views import *
from .forms import LeadForm
from django.db.models import Q
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
    leads = Lead.objects.filter(staff=user)
    query = request.GET.get('q', '')  
 
    if query:
        leads = leads.filter(
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query)
        )

    return render(request, 'lead/lead.html', {'leads': leads, 'query': query})


############################# Lead Details(Individual) ##################################
@login_required
@api_view(['POST', 'GET'])
@user_passes_test(is_User_or_Manager)
def lead_detail(request, lead_id):
    try:
        lead = get_object_or_404(Lead, id=lead_id)
    except Http404:
        return redirect('lead-view') 
    if request.method == 'POST':
        form = LeadForm(request.POST, instance=lead, user = request.user)
        if form.is_valid():
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Lead Details are updated",
                ip_address=user_details['ip_address']
            )
            form.save()
            return redirect('lead-view')
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
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"New Lead is created",
                ip_address=user_details['ip_address']
            )
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
    user_details = get_user_details(request)
    create_audit_log(
        username=user_details['username'],
        user_company=user_details['user_company'],
        group=user_details['group_names'],
        description=f"Lead is Deleted ",
        ip_address=user_details['ip_address']
    )
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
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Lead details are Updated",
                ip_address=user_details['ip_address']
            )
            form.save()
            return redirect('company_lead_list')
        else:
            print(form.errors)
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
    user_details = get_user_details(request)
    create_audit_log(
        username=user_details['username'],
        user_company=user_details['user_company'],
        group=user_details['group_names'],
        description=f"Lead is Deleted",
        ip_address=user_details['ip_address']
    )
    lead.delete()
    return redirect('company_lead_list')

################################# THE-END #################################################