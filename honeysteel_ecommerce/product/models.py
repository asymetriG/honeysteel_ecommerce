from django.db import models
from customer.models import Customer

# Create your models here.
class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=255,null=True,blank=True)
    stock = models.PositiveIntegerField(null=True,blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)

    def __str__(self):
        return self.product_name

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders",null=True,blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders",null=True,blank=True)
    quantity = models.PositiveIntegerField(null=True,blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    order_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    order_status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='PENDING',null=True,blank=True)
    progress = models.FloatField(default=0.0)

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.customer_name}"