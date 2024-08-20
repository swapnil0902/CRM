from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"crm_home/index.html")

<<<<<<< HEAD
def dashboard(request):
    return render(request, "crm/dashboard.html")
=======
def my_profile(request):
    return render(request,"crm_home/my_profile.html")
>>>>>>> f28fe03cce8e8b986914811a34557360ded2101a
