from django.db import models
from crm_home.models import Company
from django.contrib.auth.models import User
# Create your models here.

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
    staff = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    def _str_(self):
        return f'{self.first_name} {self.last_name}'