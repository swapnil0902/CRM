from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"crm_home/index.html")

def dashboard(request):
    return render(request, "crm/dashboard.html")

def my_profile(request):
    return render(request,"crm_home/my_profile.html")

