from django.db import models
from accounts.models import CustomUser
import uuid

from django.db import models
from accounts.models import CustomUser

class Order(models.Model):
    STATUS_CHOICES = [
        ('Новый', 'Новый'),
        ('Ожидает забор', 'Забрали'),
        ('Оценка', 'Оценка'),
        ('Чистка', 'Чистка'),
        ('Готов к возврату', 'Готов к возврату'),
        ('Доставлен клиенту', 'Доставлен клиенту'),
        ('Завершён', 'Завершён'),
        ('Отменён', 'Отменён'),
        ('Ошибка', 'Ошибка в данных / требует уточнения'),
    ]

    client = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='orders',
        limit_choices_to={'role': 'CLIENT'}
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='Новый'
    )
    delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата доставки"
    )

    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rug_count = models.PositiveIntegerField(default=1, verbose_name="Количество ковров")

    def __str__(self):
        return f"Заказ #{self.id} — {self.client.full_name or self.client.phone} [{self.status}]"


class Rug(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='rugs')
    rug_type = models.CharField(max_length=100)
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    condition_before = models.TextField(blank=True)


    def __str__(self):
        return f"Ковер #{self.id} для {self.order}"

class Employee(models.Model):
    full_name = models.CharField(max_length=100)
    position = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)

    def __str__(self):
        return self.full_name

class OrderStaff(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.employee} на заказ {self.order}"



class AccessToken(models.Model):
    client = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return f"Token for {self.client.username}"

class Notification(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.message}"

class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.created_at}] {self.user}: {self.message}"
