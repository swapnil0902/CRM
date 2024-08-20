from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

class Company(models.Model):
    name = models.CharField(max_length=255)
    staff = models.ManyToManyField(User, related_name='companies')
    service = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    def clean(self):
        # Custom validation to ensure a user can only belong to one company
        for user in self.staff.all():
            if user.company.exists() and user.company.first() != self:
                raise ValidationError(f"{user.username} is already assigned to another company.")
    
    def save(self, *args, **kwargs):
        self.clean()  # Ensure the validation runs before saving
        super().save(*args, **kwargs)

@receiver(post_delete, sender=User)
def delete_user_from_companies(sender, instance, **kwargs):
    instance.companies.clear()