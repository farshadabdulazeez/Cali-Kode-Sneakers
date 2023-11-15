from django.urls import path
from . import views

urlpatterns = [
    path('', views.order, name = "order"),
    path('order-page-add-address/<int:id>', views.order_page_add_address, name ="order_page_add_address"),
    path('order-page-edit-address/<int:id>', views.order_page_edit_address, name ="order_page_edit_address"),
    path('proceed-to-pay/', views.proceed_to_pay, name="proceed_to_pay"),
    path('online-payment/', views.online_payment, name = "online_payment"),
    path('order-confirmed/<str:order_id>/', views.order_confirmed, name = "order_confirmed"),
    path('order-confirmed/', views.order_confirmed, name = "order_confirmed"),
    path('order-confirmed-online/', views.order_confirmed_online, name = "order_confirmed_online"),
]