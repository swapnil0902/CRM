# models.py
from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer
from django.utils import timezone


class Appointment(models.Model):
    title = models.CharField(max_length=100,blank=False)
    description = models.TextField(blank=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(default=timezone.now)
    location = models.CharField(max_length=255, blank=True)
    attendees = models.ManyToManyField(User, related_name='appointments', blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null = False, default=7)

    def __str__(self):
        return self.title
