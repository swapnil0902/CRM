from django.db import models
from django.contrib.auth.models import User
from customer.models import Customer
from django.utils import timezone
# Create your models here.


class Task(models.Model):

    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    )
    STATUS_CHOICES = (
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    )


    id = models.AutoField(primary_key=True)
    client_name = models.CharField(max_length=100, null = False)
    title = models.CharField(max_length=100, null = False)
    description = models.CharField(max_length=500)
    due_date = models.DateField(default=timezone.now)
    due_time = models.TimeField(default=timezone.now)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)