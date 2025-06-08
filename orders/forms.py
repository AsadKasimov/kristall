from .models import Order, Rug, Employee

from accounts.models import CustomUser
from django import forms

import uuid
from django import forms
from accounts.models import CustomUser
from django.core.exceptions import ValidationError
from django import forms
from accounts.models import CustomUser
from .models import Order


class AssignEmployeeForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())


class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['full_name', 'phone', 'email', 'address']
        labels = {
            'full_name': 'ФИО клиента',
            'phone': 'Телефон',
            'email': 'Email',
            'address': 'Адрес проживания',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 '
                         'focus:ring-blue-500'
            })

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if CustomUser.objects.filter(phone=phone).exists():
            raise forms.ValidationError("Клиент с таким телефоном уже зарегистрирован.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = f"client-{uuid.uuid4().hex[:8]}"
        user.role = 'CLIENT'
        user.set_unusable_password()
        if commit:
            user.save()
        return user


from django import forms
from orders.models import Order
from accounts.models import CustomUser

class OrderForm(forms.ModelForm):
    client_phone = forms.CharField(label="Телефон клиента")
    client_address = forms.CharField(label="Адрес клиента", required=False)

    delivery_date = forms.DateField(
        label="Дата доставки",
        required=False,
        input_formats=["%d.%m.%Y"],
        widget=forms.TextInput(attrs={
            "placeholder": "дд.мм.гггг",
            "class": "w-full border rounded px-3 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        })
    )

    courier = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='COURIER'),
        label="Курьер",
        required=False
    )

    class Meta:
        model = Order
        fields = ['delivery_date', 'courier']
        labels = {
            'delivery_date': 'Дата доставки',
            'courier': 'Курьер',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                'class',
                'w-full border rounded px-3 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500'
            )


class RugForm(forms.ModelForm):
    class Meta:
        model = Rug
        exclude = ['order']
        fields = ['order', 'width', 'length']
        labels = {
            'rug_type': 'Тип ковра',
            'width': 'Ширина (м)',
            'length': 'Длина (м)',
            'condition_before': 'Состояние',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'border rounded px-3 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500'
            })


class AssignEvaluatorForm(forms.Form):
    evaluator = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='EVALUATOR'),
        label='Оценщик ковра'
    )
