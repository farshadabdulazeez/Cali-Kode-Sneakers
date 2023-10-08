from django.urls import path, reverse_lazy
from user_app import views
# from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
# from user_app.forms import MyPasswordChangeForm

urlpatterns = [

    path('', views.index, name = "index"),
    path('register/', views.register, name = "register"),
    path('user-login/', views.user_login, name = "user_login"),
    path('otp-verification/<int:user_id>/', views.otp_verification, name ="otp_verification"),
    # path('regenerate-otp/<int:id>/', views.regenerate_otp, name ="regenerate_otp"),
    path('user-profile/', views.user_profile, name ="user_profile"),
    path('add-address/<int:id>', views.add_address, name ="add_address"),
    path('edit-address/<int:id>/', views.edit_address, name ="edit_address"),
    path('delete-address/<int:address_id>/', views.delete_address, name = "delete_address"),
    # path('forgot-password/', views.forgot_password, name = "forgot_password"),
    # path('reset-password/<token>/', views.change_password, name = "reset_password"),
    # path('wallet-book/', views.wallet_book, name = "wallet_book"),
    path('user-logout/', views.user_logout, name = "user_logout"),


    # # class based views password changing
    # path('change-password/', PasswordChangeView.as_view(
    #     template_name='user/change_password.html',
    #     success_url=reverse_lazy('password_change_done'),
    #     form_class=MyPasswordChangeForm,
    # ), name="password_change"),

    # path('password-changed/', PasswordChangeDoneView.as_view(
    #     template_name='user/user_profile.html',
    # ), name="password_change_done"),

    # path('subscribe/', views.subscribe, name="subscribe"),
    # path('test/', views.test, name='test'),

]