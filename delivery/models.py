from django.db import models
from orders.models import Order, Employee



class Delivery(models.Model):
    DELIVERY_TYPE_CHOICES = [
        ('PICKUP', 'Забор'),
        ('RETURN', 'Возврат'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='deliveries')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='deliveries')
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPE_CHOICES)
    delivery_time = models.DateTimeField()

    def __str__(self):
        return f"{self.delivery_type} для {self.order}"
