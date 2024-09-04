from account.views import *
from django.db.models import Q
from .forms import CustomerForm
from django.shortcuts import render
from customer.models import Customer
from .serializers import CustomerSerializer
from rest_framework.decorators import api_view
from rest_framework.viewsets import ModelViewSet
from django.http import HttpResponseNotAllowed, Http404
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from django.contrib.auth.decorators import login_required,user_passes_test


#create your views here

############################### API ##############################################

class CustomerList(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = (IsAuthenticated,IsAdminUser)


######################## Customer Lists ##########################################
@login_required
@user_passes_test(is_User_or_Manager)
def customer_list(request):
    customers = Customer.objects.filter(staff=request.user)
    query = request.GET.get('q', '')  
 
    if query:
        customers = customers.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone_number__icontains=query) |
            Q(address__icontains=query) |
            Q(company__name__icontains=query)
        )

    return render(request, 'customer/customer.html', {'customers': customers, 'query': query})


######################## Creating Customers ######################################
@login_required
@user_passes_test(is_User_or_Manager)
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.staff = request.user  
            customer.company = request.user.userprofile.company 
            customer.save()
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"A New Customer is added ",
                ip_address=user_details['ip_address']
            )
            return redirect('customer-view')
    else:
        form = CustomerForm()
    return render(request, 'customer/customer_create.html', {'form': form})


########################  Customer Detail  ######################################
@api_view(['POST', 'GET'])
@user_passes_test(is_User_or_Manager)
def customer_detail(request, customer_id):
    try:
        customer = get_object_or_404(Customer, id=customer_id, staff=request.user)
    except Http404:
        return redirect('customer-view') 

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Customer Details are Updated",
                ip_address=user_details['ip_address']
            )
            return redirect('customer-view')
        else:
            return render(request, 'customer/customer_detail.html', {'form': form})

    elif request.method == 'GET':
        form = CustomerForm(instance=customer)
        return render(request, 'customer/customer_detail.html', {'form': form})

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    

######################## Deleting Customers ########################################## 
@api_view(['GET', 'DELETE'])
@user_passes_test(is_User_or_Manager)
def customer_delete(request, customer_id):
    lead = get_object_or_404(Customer, id=customer_id)
    user_details = get_user_details(request)
    create_audit_log(
        username=user_details['username'],
        user_company=user_details['user_company'],
        group=user_details['group_names'],
        description=f"Lead is deleted",
        ip_address=user_details['ip_address']
    )
    lead.delete()
    return redirect('customer-view')


######################## Customer Lists(Company-Wise) ################################
@login_required
@user_passes_test(is_User_or_Manager)
def company_customer_list(request):
    if not request.user.is_authenticated:
        return redirect('login')  

    company = request.user.userprofile.company
    customers = Customer.objects.filter(company=company)
    return render(request, 'customer/company_customer_list.html', {'customers': customers})


######################## Delete Customer Lists(Company-Wise) ###########################
@api_view(['GET', 'DELETE'])
@user_passes_test(is_User_or_Manager)
def company_customer_delete(request, customer_id):
    lead = get_object_or_404(Customer, id=customer_id)
    user_details = get_user_details(request)
    create_audit_log(
        username=user_details['username'],
        user_company=user_details['user_company'],
        group=user_details['group_names'],
        description=f"Lead is Deleted",
        ip_address=user_details['ip_address']
    )
    lead.delete()
    return redirect('company_customer_list')


######################## Customer Details(Company-Wise) #################################
@api_view(['POST', 'GET'])
@user_passes_test(is_User_or_Manager)
def company_customer_detail(request, customer_id):
    try:
        customer = get_object_or_404(Customer, id=customer_id)
    except Http404:
        return redirect('company_customer_list')

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            user_details = get_user_details(request)
            create_audit_log(
                username=user_details['username'],
                user_company=user_details['user_company'],
                group=user_details['group_names'],
                description=f"Customer details are updated",
                ip_address=user_details['ip_address']
            )
            form.save()
            return redirect('company_customer_detail', customer_id=customer_id)
        else:
            return render(request, 'customer/company_customer_detail.html', {'form': form})

    elif request.method == 'GET':
        form = CustomerForm(instance=customer)
        return render(request, 'customer/company_customer_detail.html', {'form': form})

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])

##################################  THE-END #############################################