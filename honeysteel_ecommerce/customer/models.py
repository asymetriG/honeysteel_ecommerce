from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=255,null=True,blank=True)
    budget = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    customer_type = models.CharField(max_length=50,null=True,blank=True)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0.0,null=True,blank=True)