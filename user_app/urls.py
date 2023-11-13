from django.urls import path, reverse_lazy
from user_app import views

urlpatterns = [

    path('', views.index, name = "index"),
    path('register/', views.register, name = "register"),
    path('user-login/', views.user_login, name = "user_login"),
    path('otp-verification/<int:user_id>/', views.otp_verification, name ="otp_verification"),
    path('forgot-password/', views.forgot_password, name = "forgot_password"),
    path('forgot-password-otp-verification/<int:user_id>/', views.forgot_password_otp_verification, name = "forgot_password_otp_verification"),
    path('update-password/<int:user_id>/', views.update_password, name = "update_password"),
    path('user-profile/', views.user_profile, name ="user_profile"),
    path('user-edit-profile/', views.user_edit_profile, name ="user_edit_profile"),
    path("order-details/<int:order_id>/", views.order_details, name="order_details"),
    path('order-cancel/<int:order_id>/', views.order_cancel, name="order_cancel"),
    path('order-return/<int:order_id>/', views.order_return, name="order_return"),
    path('order-invoice/<int:order_id>/', views.order_invoice, name="order_invoice"),
    path('add-address/<int:id>', views.add_address, name ="add_address"),
    path('edit-address/<int:id>/', views.edit_address, name ="edit_address"),
    path('delete-address/<int:address_id>/', views.delete_address, name = "delete_address"),
    path('change-password/', views.change_password, name = "change_password"),
    path('user-logout/', views.user_logout, name = "user_logout"),

]