from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
    email = models.EmailField(unique=True)
    groups = models.ManyToManyField(
        Group,
        related_name='account_user_groups',  # Custom related name to avoid clash
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='account_user_permissions',  # Custom related name to avoid clash
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

@receiver(post_save, sender=settings.AUTH_USER_MODEL) 
def createAuthToken(sender, instance, created, **kwargs):
    if created:
        Token.objects.create(user = instance)


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_token(sender, instance, **kwargs):
    Token.objects.filter(user=instance).delete()


from django.db import models
from django.contrib.auth.models import User
from crm_home.models import Company


class CustomerRequest(models.Model):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    mobile = models.IntegerField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default = 1) 
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class CompanyRequest(models.Model):
    name = models.CharField(max_length=255)
    service = models.CharField(max_length=100)
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
