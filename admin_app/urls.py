from django.urls import path 
from . import views

urlpatterns = [
    path('', views.admin_login, name = "admin_login"),
    # path('admin-dashboard/', views.admin_dashboard, name = "admin_dashboard"),

    # path('admin-users/', views.admin_users, name = "admin_users"),
    # path('admin-users-control/', views.admin_users_control, name = "admin_users_control"),

    # path('admin-category/', views.admin_category, name = "admin_category"),
    # path('admin-add-category/', views.admin_add_category, name = "admin_add_category"),
    # path('admin-edit-category/', views.admin_edit_category, name = "admin_edit_category"),

    # path('admin-products/', views.admin_products, name = "admin_products"),
    # path('admin-add-products/', views.admin_add_products, name = "admin_add_products"),
    # path('admin-edit-products/<int:id>', views.admin_edit_products, name = "admin_edit_products"),
    # path('admin-delete-products/<int:id>', views.admin_delete_products, name = "admin_delete_products"),

    # path('admin-product-variant/<int:product_id>/', views.admin_product_variant, name="admin_product_variant"),
    # path('admin-add-product-variant/<int:product_id>/', views.admin_add_product_variant, name="admin_add_product_variant"),
    # path('admin-edit-product-variant/', views.admin_edit_product_variant, name="admin_edit_product_variant"),
    # path('admin-product-variant-delete/<int:variant_id>/', views.admin_product_variant_delete, name="admin_product_variant_delete"),
    # path('admin-product-variant-control/<str:variant_id>/', views.admin_product_variant_control, name="admin_product_variant_control"),

    # path('admin-brand/', views.brand, name="admin_brand"),
    # path('admin-add-brand/', views.admin_add_brand, name="admin_add_brand"),
    # path('admin-edit-brand/<int:id>', views.admin_edit_brand, name="admin_edit_brand"),
    # path('admin-delete-brand/<int:id>', views.admin_delete_brand, name="admin_delete_brand"),

    # path('admin_logout/', views.admin_logout, name = "admin_logout"),
    
]