from django.contrib import admin
from .models import Order, Rug, Employee, OrderStaff

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'status', 'created_at', 'total_price')
    list_filter = ('status', 'created_at')
    search_fields = ('client__username',)

@admin.register(Rug)
class RugAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'width', 'length', 'calculated_price')
    readonly_fields = ('calculated_price',)
    exclude = ('rug_type', 'condition_before')

    def calculated_price(self, obj):
        if obj.width and obj.length:
            return f"{obj.width * obj.length * 350:.2f} ₽"
        return "—"
    calculated_price.short_description = "Цена (площадь × 350 ₽/м²)"

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone')

@admin.register(OrderStaff)
class OrderStaffAdmin(admin.ModelAdmin):
    list_display = ('order', 'employee')
