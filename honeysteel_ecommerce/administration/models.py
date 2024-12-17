from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class AdminUser(models.Model):
    rank = models.CharField(max_length=255,null=True,blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="adminuser",null=True,blank=True)