from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from customer.models import Customer
from .forms import CustomerForm
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseNotAllowed, Http404
from rest_framework.decorators import api_view

# @login_required
# def customer_list(request):
#     # Filter customers based on the logged-in user
#     if request.user.groups.filter(name='Account Manager').exists():
#         # If the user is an Account Manager, show customers for the Account Manager's company
#         company = request.user.userprofile.company
#         customers = Customer.objects.filter(company=company)
#     else:
#         # If the user is a Staff, show customers assigned to them
#         customers = Customer.objects.filter(staff=request.user)

#     return render(request, 'customer/customer_list.html', {'customers': customers})


@login_required
def customer_list(request):
    customers = Customer.objects.filter(staff = request.user)
    return render(request, 'customer/customer.html',{'customers': customers})


@login_required
def customer_create(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.staff = request.user  # Set the current logged-in user as staff
            customer.company = request.user.userprofile.company  # Set the company to the user's company
            customer.save()
            return redirect('customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm()

    return render(request, 'customer/customer_create.html', {'form': form})


def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    return render(request, 'customer/customer_detail.html', {'customer': customer})


@api_view(['POST', 'GET'])
def customer_detail(request, customer_id):
    try:
        customer = get_object_or_404(Customer, id=customer_id, staff=request.user)
    except Http404:
        return redirect('customer-view')  # Redirect if customer is not found or not authorized

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_detail', customer_id=customer_id)
        else:
            return render(request, 'customer/customer_detail.html', {'form': form})

    elif request.method == 'GET':
        form = CustomerForm(instance=customer)
        return render(request, 'customer/customer_detail.html', {'form': form})

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
    
    
@api_view(['GET', 'DELETE'])
def customer_delete(request, customer_id):
    lead = get_object_or_404(Customer, id=customer_id)

    lead.delete()
    return redirect('customer-view')