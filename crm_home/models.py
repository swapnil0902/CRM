from django.db import models
from django.contrib.auth.models import User

##################################          #########################################################
class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    service = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


##################################          #########################################################
class UserProfile(models.Model):
    staff = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, related_name='users', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.staff.username} - {self.company.name}"
    


