import datetime
import json
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from order.models import *
from user_app.models import *
from .models import *
from product_app.models import *
from decimal import Decimal
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
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

    total = 0
    cart_items = None
    grand_total = 0
    available_coupons = None
    selected_coupon = 0
    coupons = None  # Define coupons here

    if 'user' in request.session:
        user = request.user
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except ObjectDoesNotExist:
            pass

        try:
            cart_items = CartItem.objects.filter(customer=user).order_by('id')
            
            for item in cart_items:
                # Check if the product has a category offer
                if item.product.product.category.offer:
                    offer_percentage = item.product.product.category.offer
                    discounted_price = item.product.product.selling_price - (
                        item.product.product.selling_price * offer_percentage / 100
                    )
                    item.sub_total = Decimal(discounted_price) * Decimal(item.quantity)
                else:
                    item.sub_total = Decimal(item.product.product.selling_price) * Decimal(item.quantity)

                total += item.sub_total

            grand_total = total

            coupons = Coupons.objects.filter(active=True)

            available_coupons = Coupons.objects.filter(
                active=True,
                minimum_order_amount__lte=grand_total,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
            ).order_by('-discount')

        except ObjectDoesNotExist:
            pass
        except Exception as e:
            print(e)

    if request.method == 'POST':
        user = request.session['user']
        my_user = CustomUser.objects.get(email=user)
        orders = Order.objects.filter(user=my_user.id)
        coupon_store = [order.coupon.id for order in orders if order.coupon is not None]

        coupon_code = request.POST.get("coupon-codes")
        try:
            coupon = Coupons.objects.get(coupon_code=coupon_code)
        except Coupons.DoesNotExist:
            messages.error(request, "Invalid coupon code")
            return redirect('cart')

        if coupon.id in coupon_store:
            messages.error(request, "Coupon already used in a previous order")
            return redirect('cart')

        if not coupon.active:
            messages.error(request, "Coupon is not active")
            return redirect('cart')

        grand_total -= coupon.discount 

        request.session['selected_coupon_code'] = coupon_code
        request.session['grand_total'] = float(grand_total)

        # Update the selected_coupon variable
        selected_coupon = coupon
   
    context = {
        'quantity': quantity,
        'total': total,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'coupons': coupons,
        'available_coupons': available_coupons,
        'selected_coupon': selected_coupon
    }

    return render(request, 'cart/cart.html', context)


def add_cart_item(request, product_id):

    if not request.user.is_authenticated:
        messages.error(request, "Please log in to add items to your cart.")
        return redirect('product_details', product_id)

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
            messages.error(request, 'Invalid Size')
            return redirect('product_details', product_id) 

    # Check if the selected product variant has sufficient stock
    if variant.stock <= 0:
        messages.error(request, "This variant is out of stock.")
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
                messages.error(request, "Stock exhausted")
        else:
            cart_item = CartItem.objects.get(product=variant, cart=cart)
            if variant.stock > cart_item.quantity:
                cart_item.quantity += 1
            else:
                messages.error(request, "Stock exhausted")
        
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
    
    # Check if the product is in stock
    if cart_item.product.stock <= 0:
        messages.error(request, "This product is out of stock.")
    elif cart_item.product.stock > cart_item.quantity:
        cart_item.quantity += 1
        cart_item.save()
    else:
        messages.error(request, "Stock exhausted")

    return redirect('cart')


@cache_control(no_cache=True, no_store=True)
def remove_cart_quantity(request, cart_item_id):
    if 'email' in request.session:
        return redirect('admin_dashboard')

    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    # Check if the user is trying to decrease quantity to 0
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        messages.error(request, "Product quantity cannot be less than 1.")

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


def clear_coupon(request):
    if 'selected_coupon_code' in request.session:
        del request.session['selected_coupon_code']
        
    if 'grand_total' in request.session:
        del request.session['grand_total']

    return redirect('cart')


# def wishlist(request):
#     context = {}
#     if request.user.is_authenticated:
#         try:
#             my_user = request.user
#             user = CustomUser.objects.get(id=my_user.id)
#             wishlist_items = Wishlist.objects.filter(user=user)
            
#             # Fetching product variants associated with the wishlist items
#             product_variants = [item.variant for item in wishlist_items]

#             context = {"wishlist": wishlist_items, "product_variants": product_variants}
#             return render(request, "cart/wishlist.html", context)
#         except Exception as e:
#             print(e)
#             return render(request, "cart/wishlist.html", context)
#     else:
#         return redirect("user_login")
    

# # @login_required(login_url="index")
# # def add_to_wishlist(request, variant_id):
# #     user = request.user
# #     try:
# #         variant = ProductVariant.objects.get(id=variant_id)
# #         product_id = request.GET.get('product_id') 

# #         # You might want to validate if the product_id belongs to the variant's product here
        
# #         if Wishlist.objects.filter(user=user, variant=variant).exists():
# #             return redirect("wishlist")

# #         # Create Wishlist item associating the variant and the user
# #         wishlist = Wishlist.objects.create(user=user, variant=variant)
# #         wishlist.save()
# #         messages.success(request, "Product added to wishlist")
# #         return redirect("wishlist")
# #     except Exception as e:
# #         print(e)
# #         return redirect("index")
    

# @login_required(login_url="signin")
# def add_to_wishlist(request, variant_id):
#     variant = get_object_or_404(ProductVariant, id=variant_id)
    
#     # Check if the product is already in the wishlist for the user
#     existing_wishlist_item = Wishlist.objects.filter(user=request.user, variant=variant).first()

#     if not existing_wishlist_item:
#         # If the product is not in the wishlist, add it
#         Wishlist.objects.create(user=request.user, variant=variant)

#     return redirect('wishlist')


# @login_required(login_url="index")
# def delete_wishlist(request, wishlist_id):
#     try:
#         wishlist = Wishlist.objects.get(id=wishlist_id)
#         wishlist.delete()
#         return redirect("wishlist")
#     except Exception as e:
#         print(e)
#         return redirect("wishlist")
    

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

        try:
            address = UserAddress.objects.filter(user=my_user)
        except Exception as e:
            print(e)
            messages.error(request, "Choose address")
            return redirect('checkout')
        
        grand_total = Decimal(0)
        total = Decimal(0)

        for item in cart_items:
            # Check if the product has a category offer
            if item.product.product.category.offer:
                offer_percentage = item.product.product.category.offer
                discounted_price = item.product.product.selling_price - (
                    item.product.product.selling_price * offer_percentage / 100
                )
                total += Decimal(discounted_price) * Decimal(item.quantity)
            else:
                total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)

        grand_total = total

        selected_coupon_code = request.session.get('selected_coupon_code')

        # Check if a coupon code is selected
        if selected_coupon_code:
            try:
                # Attempt to retrieve the coupon with the specified code
                coupon = Coupons.objects.get(coupon_code=selected_coupon_code)
                grand_total -= coupon.discount
            except Coupons.DoesNotExist:
                # Handle the case where the coupon does not exist
                messages.error(request, "Selected coupon not valid")
                del request.session['selected_coupon_code']  # Clear invalid coupon from session
                return redirect('checkout')  # Redirect back to prevent processing with invalid coupon
        else:
            # No coupon selected, set coupon to None
            coupon = None

        if request.method == 'POST':
          
            try:
                delivery_address = UserAddress.objects.get(id=request.POST['delivery_address'])
            except:
                messages.error(request, "Please choose a delivery address.")
                return redirect('checkout')
            request.session['selected_address_id'] = delivery_address.id
            payment_method = request.POST['payment_method']
            
            if payment_method == "razorpayPayment":

                return redirect('online_payment')
            
            elif payment_method == "cash_on_delivery":

                user = request.user

                if 'remove_coupon' in request.POST:
                # If the user chooses to remove the coupon
                    if 'selected_coupon_code' in request.session:
                        del request.session['selected_coupon_code']  # Remove the coupon code from the session
                        # Recalculate the grand total without the coupon discount
                        grand_total = Decimal(0)
                        for item in cart_items:
                            grand_total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)
                            
                total = grand_total
                
                payment = Payments.objects.create(
                    user=user,
                    payment_method = payment_method,
                    total_amount = grand_total,
                )
                payment.save()

                order = Order.objects.create(
                    user=user, 
                    address=delivery_address,
                    payment = payment,
                    total=total,
                    order_total=grand_total, 

                )
                if coupon is not None:
                    order.coupon = coupon
                    del request.session['selected_coupon_code']
                order.save()

                # creating order with current date and order id
                yr = int(datetime.date.today().strftime('%Y'))
                dt = int(datetime.date.today().strftime('%d'))
                mt = int(datetime.date.today().strftime('%m'))
                d = datetime.date(yr, mt, dt)
                current_date = d.strftime("%Y%m%d")
                order_id = current_date + str(order.id)  # creating order id
                order.order_id = order_id

                order.save()


                cart_items = CartItem.objects.filter(customer=my_user)
                for item in cart_items:
                    variant = ProductVariant.objects.get(id=item.product.id)
                    order_item = OrderProduct.objects.create(
                        customer=my_user,
                        order_id=order,
                        payment_id=payment.id,
                        variant=variant,
                        quantity=item.quantity,
                        product_price=item.product.product.selling_price,
                        ordered=True,
                    )
                    variant.stock = variant.stock - item.quantity
                    variant.save()
                    item.delete()

                return redirect('order_confirmed', order_id )
        
            
            elif payment_method == "walletPayment":
                try:
                    user = request.user

                    # Assuming 'wallet' is the field in your user model representing the wallet balance
                    wallet_amount = user.wallet

                    # Calculate the total amount from the cart items
                    grand_total = Decimal(0)
                    for item in cart_items:
                        grand_total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)

                    # Check if the user has sufficient balance in the wallet
                    if wallet_amount >= grand_total:
                        # Deduct the amount from the wallet
                        user.wallet -= grand_total
                        user.save()

                        payment = Payments.objects.create(
                            user=user,
                            payment_method=payment_method,
                            total_amount=grand_total,
                        )
                        payment.save()

                        order = Order.objects.create(
                            user=user,
                            address=delivery_address,
                            payment=payment,
                            total=grand_total,
                            order_total=grand_total,
                        )
                        order.save()

                        # Creating order with the current date and order id
                        yr = int(datetime.date.today().strftime('%Y'))
                        dt = int(datetime.date.today().strftime('%d'))
                        mt = int(datetime.date.today().strftime('%m'))
                        d = datetime.date(yr, mt, dt)
                        current_date = d.strftime("%Y%m%d")
                        order_id = current_date + str(order.id)  # Creating order id
                        order.order_id = order_id

                        order.save()

                        # Process cart items and create order items
                        cart_items = CartItem.objects.filter(customer=my_user)
                        for item in cart_items:
                            variant = ProductVariant.objects.get(id=item.product.id)
                            order_item = OrderProduct.objects.create(
                                customer=my_user,
                                order_id=order,
                                payment_id=payment.id,
                                variant=variant,
                                quantity=item.quantity,
                                product_price=item.product.product.selling_price,
                                ordered=True,
                            )
                            variant.stock = variant.stock - item.quantity
                            variant.save()
                            item.delete()

                        return redirect('order_confirmed', order_id)

                    else:
                        # Redirect the user with an error message about insufficient funds
                        messages.error(request, "Insufficient funds in the wallet.")
                        return redirect('checkout')

                except Exception as e:
                    # Log the exception or handle it as needed
                    messages.error(request, str(e))
                    return redirect('checkout')
        
        context = {
            'addresses': address,
            'cart_items' : cart_items,
            'grand_total' : grand_total,
            'selected_coupon_code': selected_coupon_code, 
            'applied_coupon': coupon,
        }

        return render(request, "cart/checkout.html", context)