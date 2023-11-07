from django.urls import path 
from . import views

urlpatterns = [
    path('', views.admin_login, name="admin_login"),
    path('admin-dashboard/', views.admin_dashboard, name="admin_dashboard"),

    path('admin-users/', views.admin_users, name="admin_users"),
    path('admin-users-control/<int:id>', views.admin_users_control, name="admin_users_control"),

    path('admin-category/', views.admin_category, name="admin_category"),
    path('admin-add-category/', views.admin_add_category, name="admin_add_category"),
    path('admin-edit-category/<int:id>', views.admin_edit_category, name="admin_edit_category"),
    # path('admin-delete-category/<int:id>', views.admin_delete_category, name="admin_delete_category"),
    path('admin-control-category/<int:id>', views.admin_control_category, name="admin_control_category"),


    path('admin-products/', views.admin_products, name="admin_products"),
    path('admin-add-product/', views.admin_add_product, name="admin_add_product"),
    path('admin-edit-product/<int:id>', views.admin_edit_product, name="admin_edit_product"),
    path('admin-delete-product/<int:id>', views.admin_delete_product, name="admin_delete_product"),
    path('admin-control-product/<int:id>', views.admin_control_product, name="admin_control_product"),

    path('admin-product-variant/<int:product_id>/', views.admin_product_variant, name="admin_product_variant"),
    path('admin-add-product-variant/<int:product_id>/', views.admin_add_product_variant, name="admin_add_product_variant"),
    path('admin-edit-product-variant/', views.admin_edit_product_variant, name="admin_edit_product_variant"),
    path('admin-delete-product-variant/<int:variant_id>/', views.admin_delete_product_variant, name="admin_delete_product_variant"),
    path('admin-control-product-variant/<str:variant_id>/', views.admin_control_product_variant, name="admin_control_product_variant"),

    path('admin-brands/', views.admin_brands, name="admin_brands"),
    path('admin-add-brand/', views.admin_add_brand, name="admin_add_brand"),
    path('admin-edit-brand/<int:id>', views.admin_edit_brand, name="admin_edit_brand"),
    path('admin-delete-brand/<int:id>', views.admin_delete_brand, name="admin_delete_brand"),
    path('admin-control-brand/<int:id>', views.admin_control_brand, name="admin_control_brand"),

    path('admin-coupons/', views.admin_coupons, name="admin_coupons"),
    path('admin-add-coupon/', views.admin_add_coupon, name="admin_add_coupon"),
    path('admin-delete-coupon/<int:coupon_id>/', views.admin_delete_coupon, name="admin_delete_coupon"),
    path('admin-edit-coupon/<int:coupon_id>/', views.admin_edit_coupon, name="admin_edit_coupon"),
    path('admin-activate-coupon/<int:coupon_id>/', views.admin_activate_coupon, name="admin_activate_coupon"),

    path('admin-orders/', views.admin_orders, name="admin_orders"),
    path('admin-orders-detail/<int:id>/', views.admin_orders_detail, name="admin_orders_detail"),
    path('admin-orders-status/<int:id>/', views.admin_orders_status, name="admin_orders_status"),

      path('admin-banner/', views.admin_banner, name="admin_banner"),
    path('admin-edit-banner/<int:banner_id>/', views.admin_edit_banner, name="admin_edit_banner"),

    path('admin-logout/', views.admin_logout, name = "admin_logout"),

    
]