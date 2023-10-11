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


def cart(request, quantity=0, total=0, cart_items=None, grand_total=0):

    if 'email' in request.session:
        return redirect('admin_dashboard')

    quantity = 0
    total = 0
    cart_items = None
    grand_total = 0

    if 'user' in request.session:

        user = request.user
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))  # fetching the cart id

        except ObjectDoesNotExist:
            pass

        try:

            cart_items = CartItem.objects.filter(customer=user).order_by('id')   # fetch every cart items related with the cart
            for item in cart_items:                    
                total = total + (float(item.product.product.selling_price) * float(item.quantity))
                
            grand_total = total  # You can add taxes, shipping, and discounts here

        except Exception as e:
            print(e)

   
    context = {
        'quantity' : quantity,
        'total' : total,
        'cart_items' : cart_items,
        'grand_total' : grand_total,
    }

    return render(request, 'cart/cart.html', context)


def add_cart_item(request, product_id):

    product = Product.objects.get(id=product_id)
    size = None
    variant = None

    if request.method == 'POST':

        try:
            product = Product.objects.get(id=product_id)
            category_slug = product.category.slug
            product_slug = product.slug
            size = request.POST.get('size') 

            if size:
                variant = ProductVariant.objects.get(Q(product=product), Q(product_size__size=size))
            else:
                messages.error(request, 'Select a size')
                return redirect('product_details', product_id)
            
        except ProductVariant.DoesNotExist:
            return redirect('product_details', product_id)        

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
            cart_item.save()

        else:
            cart_item = CartItem.objects.create(product=variant, quantity=1, cart=cart)
            cart_item.save()
        cart.save()

    return redirect('cart')


@cache_control(no_cache=True, no_store=True)
def add_cart_quantity(request, cart_item_id):
    if 'email' in request.session:
        return redirect('admin_dashboard')
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    if cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


@cache_control(no_cache=True, no_store=True)
def remove_cart_quantity(request, cart_item_id):
    if 'email' in request.session:
        return redirect('admin_dashboard')
    
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    
    return redirect('cart')


@cache_control(no_cache=True, no_store=True)
def delete_cart_item(request, variant_id):
    if 'email' in request.session:
        return redirect('admin_dashboard')
    
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


@cache_control(no_cache=True, no_store=True)
def clear_cart(request):
    if 'email' in request.session:
        return redirect('admin_dashboard')
    
    user = request.user
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        return redirect('cart')
    
    cart_items = CartItem.objects.filter(cart=cart)
    
    for cart_item in cart_items:
        cart_item.delete()
    
    return redirect('cart')


@cache_control(no_cache=True, no_store=True)
@login_required(login_url='user_login')
def checkout(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        my_user = request.user
        cart_items = CartItem.objects.filter(customer=my_user)

        if not cart_items:
            return redirect('index')
        checkout_user = my_user.id

        try:
            address = UserAddress.objects.filter(user=my_user)

        except Exception as e:
            print(e)
            messages.error(request, "choose address")
            return redirect('checkout')
        
        total = 0
        grand_total = 0

        cart_items = CartItem.objects.filter(customer=my_user).order_by('id')

        for item in cart_items:
            total = total + (float(item.product.product.selling_price) * float(item.quantity))
        grand_total = total            
        
        context = {
            'addresses': address,
            'cart_items' : cart_items,
            'grand_total' : grand_total,
        }

        return render(request, "cart/checkout.html", context)