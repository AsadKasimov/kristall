from django.contrib import admin
from .models import Order, Rug, Employee, OrderStaff

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username',)

@admin.register(Rug)
class RugAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'rug_type', 'condition_before')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone')

@admin.register(OrderStaff)
class OrderStaffAdmin(admin.ModelAdmin):
    list_display = ('order', 'employee')
