from django.db import models
from django.conf import settings
from django.utils import timezone
from crm_home.models import Company
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save, post_delete


##################################          #########################################################
@receiver(post_save, sender=settings.AUTH_USER_MODEL) 
def createAuthToken(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user = instance)


##################################          #########################################################
@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_token(sender, instance, **kwargs):
    Token.objects.filter(user=instance).delete()


##################################          #########################################################
class UserRequest(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default = 1) 
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


##################################          #########################################################
class CompanyRequest(models.Model):
    name = models.CharField(max_length=255)
    service = models.CharField(max_length=100)
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

##################################          #########################################################

class AuditLogDetails(models.Model):
    user_name = models.CharField(max_length=150)
    user_company = models.CharField(max_length=255) 
    group = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)  
    timestamp = models.DateTimeField(default=timezone.now)
    description=models.CharField(max_length=500) 

    def __str__(self):
        return f"AuditLog({self.username}, {self.user_company}, {self.group}, {self.timestamp})"
