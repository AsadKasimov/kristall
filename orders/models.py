from django.db import models
from django.utils import timezone

from accounts.models import CustomUser
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ('Новый', 'Новый'),
        ('Забрали', 'Забрали'),
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
    return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата возврата"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rug_count = models.PositiveIntegerField(default=1, verbose_name="Количество ковров")
    courier = models.ForeignKey(
        'accounts.CustomUser',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='courier_orders',
        limit_choices_to={'role': 'COURIER'},
        verbose_name='Курьер'
    )

    def __str__(self):
        return f"Заказ #{self.id} — {self.client.full_name or self.client.phone} [{self.status}]"

class Rug(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='rugs')
    width = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    length = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Ковер #{self.id} для {self.order}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Пересчёт total_price заказа
        total = 0
        for rug in self.order.rugs.all():
            if rug.width and rug.length:
                total += float(rug.width) * float(rug.length) * 350
        self.order.total_price = total
        self.order.save()


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

import uuid
from django.db import models

class AccessToken(models.Model):
    client = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'CLIENT'})
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    short_token = models.CharField(max_length=16, unique=True, blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.short_token:
            self.short_token = str(self.token).replace('-', '')[:8]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.short_token



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

class Courier(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'COURIER'})
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.full_name or self.user.username}"

class ShiftLog(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'date')
