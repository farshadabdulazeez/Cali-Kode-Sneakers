from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from user_app.models import *
from .models import *
from product_app.models import *
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required


def _cart_id(request):

    cart = request.session.session_key  # checking for current session
    
    if not cart:
        cart = request.session.create()  # if there is no session create a new session
    return cart


def cart(request, quantity=0, total=0, cart_items=None):

    total = 0
    quantity = 0


    return render(request, 'cart/cart.html')


def add_cart(request, product_id):

    product = Product.objects.get(id=product_id)

    # getting variant of product
    if request.method == 'POST':
        try:
            product = Product.objects.get(id=product_id)
            category_slug = product.category.slug
            product_slug = product.slug
            size = request.POST['size']
            if size:
                variant = ProductVariant.objects.get(Q(product=product), Q(product_size__size=size))
            else:
                messages.error(request, 'choose a size')
                return redirect('product_details', category_slug, product_slug)
        except ProductVariant.DoesNotExist:
            return redirect('product_details', category_slug, product_slug)

    # getting cart    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))   #to get the cart using cart id present in the session
        cart.save()

    # getting cart items
    try:
        if 'user' in request.session:
            my_user = request.user
            cart_item = CartItem.objects.get(product=variant, customer=my_user)
            if variant.stock > cart_item.quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, "stock exhausted")
        else:
            cart_item = CartItem.objects.get(product=variant, cart=cart)
            if variant.stock > cart_item.quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, "stock exhausted")
        cart_item.save()


    except CartItem.DoesNotExist:
        if 'user' in request.session:
            my_user = request.user
            cart_item = CartItem.objects.create(product=variant, quantity=1, cart=cart, customer=my_user)
        else:
            cart_item = CartItem.objects.create(product=variant, quantity=1, cart=cart)
        cart.save()

    return redirect('cart')


# @cache_control(no_cache=True, no_store=True)
def delete_cart(request, variant_id):
    # if 'email' in request.session:
    #     return redirect('admin_dashboard')
    variant = get_object_or_404(ProductVariant, id=variant_id)

    if 'user' in request.session:
        my_user = request.user
        cart_item = CartItem.objects.filter(customer=my_user, product=variant)

        if cart_item:
            cart_item.delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.filter(cart=cart, product=variant)
        cart_item.delete()
        
    return redirect('cart')