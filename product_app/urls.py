from django.urls import path 
from . import views

urlpatterns = [

    path('', views.products, name="products"),
    path('product-details/<int:id>/', views.product_details, name="product_details"),
    path('category/<slug:category_slug>/', views.products, name="products_by_category"),
    path('product-search/', views.product_search, name="product_search"),
    # path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name="product_details"),
     
]