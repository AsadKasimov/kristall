from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'employee', 'delivery_type', 'delivery_time')
    list_filter = ('delivery_type',)
