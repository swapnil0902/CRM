from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Appointment(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return self.name