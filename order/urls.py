from django.urls import path
from . import views

urlpatterns = [
    path('', views.order, name = "order"),
    path('order-confirmed/', views.order_confirmed, name = "order_confirmed"),
]