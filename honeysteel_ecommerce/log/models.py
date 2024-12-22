from django.db import models
from customer.models import Customer
from product.models import Order
from django.utils.timezone import now

class Log(models.Model):
    LOG_TYPE_CHOICES = [
        ('INFO', 'Info'),
        ('ERROR', 'Error'),
        ('WARNING', 'Warning'),
    ]

    log_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="logs", null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logs", null=True, blank=True)
    log_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    log_type = models.CharField(max_length=10, choices=LOG_TYPE_CHOICES, default='INFO', null=True, blank=True)
    log_details = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Log {self.log_id} - {self.log_type}"

    @staticmethod
    def save_log(log_type, log_details, customer=None, order=None):
        """
        Save a log entry with the given details.
        
        :param log_type: The type of log (INFO, ERROR, WARNING).
        :param log_details: Details about the log.
        :param customer: The associated customer (optional).
        :param order: The associated order (optional).
        """
        log_entry = Log(
            log_type=log_type,
            log_details=log_details,
            customer=customer,
            order=order,
            log_date=now()  # Use the current timestamp
        )
        log_entry.save()


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
    
    
    @staticmethod
    def save_log(log_type, log_details, customer=None, order=None):
        """
        Save a log entry with the given details.
        
        :param log_type: The type of log (INFO, ERROR, WARNING).
        :param log_details: Details about the log.
        :param customer: The associated customer (optional).
        :param order: The associated order (optional).
        """
        log_entry = Log(
            log_type=log_type,
            log_details=log_details,
            customer=customer,
            order=order,
            log_date=now()  # Use the current timestamp
        )
        log_entry.save()