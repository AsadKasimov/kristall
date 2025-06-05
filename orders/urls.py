from django.urls import path

from . import views
from .views import client_dashboard, operator_order_list, edit_order, operator_dashboard, client_search_view
from .views import order_success
from .views import create_client_view, create_order_with_client
from django.contrib.auth.views import LogoutView

from .views import create_order
from .views import faq_view
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('dashboard/<uuid:token>/', client_dashboard, name='client_dashboard'),
    path('faq/', faq_view, name='faq'),
    path('operator/create/', create_order, name='create_order'),

    path('operator/success/<int:order_id>/', order_success, name='order_success'),
    path('operator/orders/', operator_order_list, name='operator_order_list'),

    path('operator/edit/<int:order_id>/', edit_order, name='edit_order'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('operator/', operator_dashboard, name='operator_dashboard'),
    path('operator/orders/create/', create_order, name='create_order'),
    path('operator/clients/create/', create_client_view, name='create_client'),
    path('operator/orders/create/<int:client_id>/', create_order_with_client, name='create_order_with_client'),
    path('api/client-search/', client_search_view, name='client_search'),
    path('api/get_client_address/', views.get_client_address, name='get_client_address'),
    path('d/<str:short_token>/', views.short_dashboard_redirect, name='short_dashboard'),
    path("go/", views.redirect_by_token, name="redirect_by_token"),
    path('courier/', views.courier_dashboard, name='courier_dashboard'),
    path('courier/mark-picked-up/<int:order_id>/', views.mark_picked_up, name='mark_picked_up'),
    path('courier/mark-delivered/<int:order_id>/', views.mark_delivered, name='mark_delivered'),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("api/courier-load/", views.get_courier_load, name="courier_load"),
]










