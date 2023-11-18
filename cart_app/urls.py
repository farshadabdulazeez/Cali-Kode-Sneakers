from django.urls import path 
from . import views

urlpatterns = [

    path('', views.cart, name = "cart"),
    path('add-cart-item/<int:product_id>/', views.add_cart_item, name="add_cart_item"),
    path('add-cart-quantity/<int:cart_item_id>/', views.add_cart_quantity, name="add_cart_quantity"),
    path('remove-cart-quantity/<int:cart_item_id>/', views.remove_cart_quantity, name="remove_cart_quantity"),
    path('delete-cart-item/<int:variant_id>/', views.delete_cart_item, name="delete_cart_item"),
    path('clear-cart/', views.clear_cart, name="clear_cart"), 
    path('clear-coupon/', views.clear_coupon, name="clear_coupon"), 
    # path('wishlist/', views.wishlist, name="wishlist"), 
    # path('add-to-wishlist/<int:variant_id>/', views.add_to_wishlist, name="add_to_wishlist"),
    # path('delete-wishlist/<int:wishlist_id>/', views.delete_wishlist, name="delete_wishlist"),
    path('checkout/', views.checkout, name="checkout"),
    
]