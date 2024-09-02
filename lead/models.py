from django.db import models
from django.urls import reverse
from urllib.parse import urlencode
from crm_home.models import Company
from django.dispatch import receiver
from customer.models import Customer
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db.models.signals import post_save



# Create your models here.
#############################   Lead Model   #############################################################
class Lead(models.Model):
    STATUS_CHOICES = (
        ('Not Contacted', 'Not Contacted'),
        ('Contacted', 'Contacted'),
        ('Converted to Customer', 'Converted to Customer'),
    )
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    status = status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'



#############################        #############################################################
@receiver(post_save, sender=Lead)
def handle_lead_status_change(sender, instance, **kwargs):
    if instance.status == 'Converted to Customer':
        Customer.objects.create(
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
            phone_number=instance.phone_number,
            address=instance.address,
            company=instance.company,
            staff=instance.staff
        )

        instance.delete()

        url = reverse('lead-view')
        query_params = urlencode({'alert': 'true'})
        full_url = f"{url}?{query_params}"

        return redirect(full_url)

#############################        #############################################################