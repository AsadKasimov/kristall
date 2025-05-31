from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Order, Notification

@receiver(post_save, sender=Order)
def notify_client_on_order_update(sender, instance, created, **kwargs):
    if not created:
        recent = Notification.objects.filter(
            user=instance.client,
            order=instance,
            message__icontains=f"«{instance.status}»",
            created_at__gte=now() - timedelta(minutes=2)
        )
        if not recent.exists():
            Notification.objects.create(
                user=instance.client,
                order=instance,
                message=f"Статус вашего заказа #{instance.id} изменён на «{instance.status}»"
            )
