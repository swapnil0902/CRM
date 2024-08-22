from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    service = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    staff = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='users', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.staff.username} - {self.company.name}"
    


