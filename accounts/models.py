from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('CLIENT', 'Клиент'),
        ('OPERATOR', 'Оператор'),
        ('EVALUATOR', 'Оценщик')
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name or self.username} ({self.role})"
