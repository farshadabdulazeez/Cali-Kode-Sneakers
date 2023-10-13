from django.urls import path
from . import views

urlpatterns = [
    path('', views.order, name = "order"),
    path('online-payment/', views.online_payment, name = "online_payment"),
    path('order-confirmed/', views.order_confirmed, name = "order_confirmed"),
    path('proceed-to-pay/', views.proceed_to_pay, name="proceed_to_pay"),
]