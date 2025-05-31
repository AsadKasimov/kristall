from django.shortcuts import render, get_object_or_404
from django import forms
from django.forms import inlineformset_factory
from accounts.models import CustomUser
from .models import AccessToken, Order, Rug, Notification
from django.shortcuts import redirect
from .models import AccessToken, OrderStaff
from .forms import OrderForm, RugForm, AssignEmployeeForm
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import HttpResponse
from .models import OrderLog
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from .forms import ClientCreateForm
from accounts.models import CustomUser
from .models import AccessToken
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from accounts.models import CustomUser
from django.db.models import Q
from django.forms import formset_factory
from django.forms.formsets import DELETION_FIELD_NAME
from django.utils.timezone import now

from django.http import JsonResponse
from accounts.models import CustomUser

def client_dashboard(request, token):
    access_token = get_object_or_404(AccessToken, token=token)
    client = access_token.client
    orders = client.orders.all().order_by('-created_at')

    return render(request, 'orders/dashboard.html', {
        'client': client,
        'orders': orders,
    })


def faq_view(request):
    return render(request, 'orders/faq.html')


@login_required
def create_order(request):
    RugFormSet = modelformset_factory(Rug, form=RugForm, extra=2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        rug_forms = RugFormSet(request.POST, queryset=Rug.objects.none())
        emp_form = AssignEmployeeForm(request.POST)

        if form.is_valid() and rug_forms.is_valid() and emp_form.is_valid():
            order = form.save()
            for rug_form in rug_forms:
                rug = rug_form.save(commit=False)
                rug.order = order
                rug.save()
            OrderStaff.objects.create(order=order, employee=emp_form.cleaned_data['employee'])

            # создаём токен
            AccessToken.objects.get_or_create(client=order.client)

            return redirect('order_success', order_id=order.id)

    else:
        form = OrderForm()
        rug_forms = RugFormSet(queryset=Rug.objects.none())
        emp_form = AssignEmployeeForm()

    return render(request, 'orders/create_order.html', {
        'form': form,
        'rug_forms': rug_forms,
        'emp_form': emp_form,
    })


@login_required
def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    token = AccessToken.objects.get(client=order.client)
    url = request.build_absolute_uri(f"/dashboard/{token.token}/")
    return HttpResponse(f"✅ Заказ создан! Ссылка для клиента: <a href='{url}'>{url}</a>")


@login_required
def operator_order_list(request):
    orders = Order.objects.select_related('client').prefetch_related('rugs').order_by('-created_at')
    return render(request, 'orders/operator_list.html', {'orders': orders})





@login_required
def operator_order_list(request):
    status_filter = request.GET.get('status')
    search = request.GET.get('q')

    orders = Order.objects.select_related('client').prefetch_related('rugs').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    if search:
        orders = orders.filter(client__username__icontains=search)

    statuses = Order.objects.values_list('status', flat=True).distinct()

    return render(request, 'orders/operator_list.html', {
        'orders': orders,
        'statuses': statuses,
        'active_status': status_filter,
        'search': search,
    })


def only_operators(view_func):
    def wrapped(request, *args, **kwargs):
        if request.user.role != 'OPERATOR':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped


def index(request):
    return render(request, 'index.html')


def token_redirect(request):
    token = request.GET.get('token')
    if token:
        return redirect(f"/dashboard/{token}/")
    return redirect('/')


from django.shortcuts import render


def faq_view(request):
    return render(request, 'orders/faq.html')

@login_required
@only_operators
def operator_dashboard(request):
    return render(request, 'orders/operator_dashboard.html')


@login_required
@only_operators
def create_order_with_client(request, client_id):
    client = get_object_or_404(CustomUser, id=client_id, role='CLIENT')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.client = client
            order.save()
            return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm(initial={'status': 'Новый'})

    return render(request, 'orders/create_order.html', {
        'form': form,
        'client': client,
    })





@login_required
@only_operators
def create_client_view(request):
    if request.method == 'POST':
        form = ClientCreateForm(request.POST)
        if form.is_valid():
            client = form.save()
            token, _ = AccessToken.objects.get_or_create(client=client)
            return redirect('create_order_with_client', client_id=client.id)
    else:
        form = ClientCreateForm()
    return render(request, 'orders/create_client.html', {'form': form})

@login_required
@only_operators
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['client_phone']
            try:
                client = CustomUser.objects.get(phone=phone, role='CLIENT')
            except CustomUser.DoesNotExist:
                form.add_error('client_phone', 'Клиент с таким телефоном не найден.')
            else:
                order = form.save(commit=False)
                order.client = client
                order.save()

                # Обновим адрес клиента, если он изменился
                new_address = form.cleaned_data.get("client_address")
                if new_address and new_address != client.address:
                    client.address = new_address
                    client.save()

                return redirect('order_success', order_id=order.id)
    else:
        form = OrderForm(initial={'status': 'Новый'})

    return render(request, 'orders/create_order.html', {'form': form})

class OrderEditForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ['client']
        labels = {
            'status': 'Статус',
            'total_price': 'Общая стоимость',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full border rounded px-3 py-2 bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500'
            })




from django.forms import formset_factory
from .forms import RugForm
from django.utils.timezone import now, localtime
from datetime import timedelta

@login_required
@only_operators
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    RugFormSet = formset_factory(RugForm, extra=0, can_delete=True)
    existing_rugs = Rug.objects.filter(order=order)
    empty_rug_form = None

    if request.method == 'POST':
        old_status = order.status
        form = OrderEditForm(request.POST, instance=order)
        rug_forms = RugFormSet(request.POST)

        if form.is_valid() and rug_forms.is_valid():
            form.save()
            order.rugs.all().delete()

            valid_forms = [
                f for f in rug_forms.forms
                if not f.cleaned_data.get('DELETE') and (
                    f.cleaned_data.get('rug_type') or f.cleaned_data.get('width') or f.cleaned_data.get('length')
                )
            ]

            order.rug_count = len(valid_forms)
            order.save()

            for rug_form in valid_forms:
                rug = rug_form.save(commit=False)
                rug.order = order
                rug.save()

            if order.status != old_status:
                now_local = localtime(now())

                already_exists = Notification.objects.filter(
                    user=order.client,
                    order=order,
                    message=f"Статус вашего заказа #{order.id} изменён на «{order.status}»"
                ).order_by('-created_at').first()

                if not already_exists or (now_local - already_exists.created_at).total_seconds() > 180:
                    Notification.objects.create(
                        user=order.client,
                        order=order,
                        message=f"Статус вашего заказа #{order.id} изменён на «{order.status}»"
                    )

            return redirect('operator_order_list')
    else:
        initial_data = list(existing_rugs.values('rug_type', 'width', 'length', 'condition_before'))
        rug_forms = RugFormSet(initial=initial_data)
        empty_rug_form = rug_forms.empty_form
        form = OrderEditForm(instance=order)

    return render(request, 'orders/edit_order.html', {
        'form': form,
        'rug_forms': rug_forms,
        'empty_form': empty_rug_form,
        'order': order
    })







@login_required
def client_search_view(request):
    query = request.GET.get('q', '')
    results = []

    if query:
        clients = CustomUser.objects.filter(
            role='CLIENT',
            phone__icontains=query
        )[:10]

        results = [{
            'id': client.id,
            'label': f"{client.phone} — {client.full_name}",
            'phone': client.phone
        } for client in clients]

    return JsonResponse(results, safe=False)


@login_required
def get_client_address(request):
    phone = request.GET.get("phone")
    try:
        client = CustomUser.objects.get(phone=phone, role="CLIENT")
        return JsonResponse({"address": client.address})
    except CustomUser.DoesNotExist:
        return JsonResponse({"address": ""})
