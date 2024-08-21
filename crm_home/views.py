from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request,"crm_home/index.html")

def dashboard(request):
    return render(request, "crm/dashboard.html")

def my_profile(request):
    return render(request,"crm_home/my_profile.html")


# from django.db import connection

# def get_company_id(user_id):
#     cursor = connection.cursor()
#     cursor.execute("SELECT company_id FROM crm_home_company_staff WHERE staff_id = %s", [user_id])
#     company_id = cursor.fetchone()[1]  # Assuming company_id is the second column
#     return company_id
