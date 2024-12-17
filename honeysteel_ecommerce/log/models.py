from django.db import models
from customer.models import Customer
from product.models import Order

# Create your models here.
class Log(models.Model):
    LOG_TYPE_CHOICES = [
        ('INFO', 'Info'),
        ('ERROR', 'Error'),
        ('WARNING', 'Warning'),
    ]

    log_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="logs",null=True,blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logs", null=True, blank=True)
    log_date = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES, default='INFO',null=True,blank=True)
    log_details = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"Log {self.log_id} - {self.log_type}"