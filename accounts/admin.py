from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from django import forms
from django.contrib.auth.forms import UserCreationForm

@admin.action(description="Сделать операторами")
def set_operator(modeladmin, request, queryset):
    queryset.update(role='OPERATOR')


# 👇 Форма создания пользователя с полем phone
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "phone", "password1", "password2")


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm

    list_display = ("full_name", "username", "role", "email", "phone")  # 👈 добавили full_name
    fieldsets = UserAdmin.fieldsets + (
        (None, {"fields": ("role", "phone", "address", "full_name")}),  # 👈 добавили full_name
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'phone', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )
    actions = [set_operator]

