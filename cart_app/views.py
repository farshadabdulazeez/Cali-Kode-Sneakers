import datetime
import json
import logging
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


# Helper function to get or create a cart session key
def _cart_id(request):
    cart = request.session.session_key  # checking for current session
    if not cart:
        cart = request.session.create()  # if there is no session create a new session
    return cart


# def cart(request, quantity=0, total=0, cart_items=None, grand_total=0):

#     if 'email' in request.session:
#         return redirect('admin_dashboard')

#     total = 0
#     cart_items = None
#     grand_total = 0
#     available_coupons = None
#     selected_coupon = 0
#     coupons = None  # Define coupons here

#     if 'user' in request.session:
#         user = request.user
#         try:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#         except ObjectDoesNotExist:
#             pass

#         try:
#             cart_items = CartItem.objects.filter(customer=user).order_by('id')
            
#             for item in cart_items:
#                 # Check if the product has a category offer
#                 if item.product.product.category.offer:
#                     offer_percentage = item.product.product.category.offer
#                     discounted_price = item.product.product.selling_price - (
#                         item.product.product.selling_price * offer_percentage / 100
#                     )
#                     item.sub_total = Decimal(discounted_price) * Decimal(item.quantity)
#                 else:
#                     item.sub_total = Decimal(item.product.product.selling_price) * Decimal(item.quantity)

#                 total += item.sub_total

#             grand_total = total

#             coupons = Coupons.objects.filter(active=True)

#             available_coupons = Coupons.objects.filter(
#                 active=True,
#                 minimum_order_amount__lte=grand_total,
#                 valid_from__lte=timezone.now(),
#                 valid_to__gte=timezone.now()
#             ).order_by('-discount')

#         except ObjectDoesNotExist:
#             pass
#         except Exception as e:
#             print(e)

#     if request.method == 'POST':
#         user = request.session['user']
#         my_user = CustomUser.objects.get(email=user)
#         orders = Order.objects.filter(user=my_user.id)
#         coupon_store = [order.coupon.id for order in orders if order.coupon is not None]

#         coupon_code = request.POST.get("coupon-codes")
#         try:
#             coupon = Coupons.objects.get(coupon_code=coupon_code)
#         except Coupons.DoesNotExist:
#             messages.error(request, "Invalid coupon code")
#             return redirect('cart')

#         if coupon.id in coupon_store:
#             messages.error(request, "Coupon already used in a previous order")
#             return redirect('cart')

#         if not coupon.active:
#             messages.error(request, "Coupon is not active")
#             return redirect('cart')

#         grand_total -= coupon.discount 

#         request.session['selected_coupon_code'] = coupon_code
#         request.session['grand_total'] = float(grand_total)

#         # Update the selected_coupon variable
#         selected_coupon = coupon
   
#     context = {
#         'quantity': quantity,
#         'total': total,
#         'cart_items': cart_items,
#         'grand_total': grand_total,
#         'coupons': coupons,
#         'available_coupons': available_coupons,
#         'selected_coupon': selected_coupon
#     }

#     return render(request, 'cart/cart.html', context)




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



# FDSHJGVD
# @cache_control(no_cache=True)
# def cart(request, quantity=0, total=0, cart_items=None, grand_total=0):
#     try:
#         # Check if the user is an admin
#         if 'email' in request.session:
#             return redirect('admin_dashboard')

#         total = 0
#         cart_items = None
#         grand_total = 0
#         available_coupons = None
#         selected_coupon = 0
#         coupons = None  # Define coupons here

#         # Check if the user is logged in
#         if 'user' in request.session:
#             user = request.user
#             try:
#                 cart = Cart.objects.get(cart_id=_cart_id(request))

#             except ObjectDoesNotExist:
#                 pass

#             try:
#                 # Get cart items for the logged-in user
#                 cart_items = CartItem.objects.filter(customer=user).order_by('id')


#                 for item in cart_items:
#                     # Check if the product has a category offer
#                     if item.product.product.category.offer:
#                         offer_percentage = item.product.product.category.offer
#                         discounted_price = item.product.product.selling_price - (
#                             item.product.product.selling_price * offer_percentage / 100
#                         )
#                         item.sub_total = Decimal(discounted_price) * Decimal(item.quantity)
#                     else:
#                         item.sub_total = Decimal(item.product.product.selling_price) * Decimal(item.quantity)

#                     total += item.sub_total

#                 grand_total = total

#                 coupons = Coupons.objects.filter(active=True)

#                 # Get available coupons based on conditions
#                 available_coupons = Coupons.objects.filter(
#                     active=True,
#                     minimum_order_amount__lte=grand_total,
#                     valid_from__lte=timezone.now(),
#                     valid_to__gte=timezone.now()
#                 ).order_by('-discount')

#             except ObjectDoesNotExist:
#                 pass
#             except Exception as e:
#                 print(e)

#         # Handle coupon application when the form is submitted (POST request)
#         if request.method == 'POST':
#             user = request.session['user']
#             my_user = CustomUser.objects.get(email=user)
#             orders = Order.objects.filter(user=my_user.id)
#             coupon_store = [order.coupon.id for order in orders if order.coupon is not None]

#             # Get coupon code from the form
#             coupon_code = request.POST.get("coupon-codes")

#             try:
#                 # Retrieve the coupon object based on the provided code
#                 coupon = Coupons.objects.get(coupon_code=coupon_code)
#             except Coupons.DoesNotExist:
#                 messages.error(request, "Invalid coupon code")
#                 return redirect('cart')

#             # Check if the coupon has already been used in a previous order
#             if coupon.id in coupon_store:
#                 messages.error(request, "Coupon already used in a previous order")
#                 return redirect('cart')

#             # Check if the coupon is active
#             if not coupon.active:
#                 messages.error(request, "Coupon is not active")
#                 return redirect('cart')

#             # Apply coupon discount to the grand total
#             grand_total -= coupon.discount

#             # Update session variables
#             request.session['selected_coupon_code'] = coupon_code
#             request.session['grand_total'] = float(grand_total)

#             # Update the selected_coupon variable
#             selected_coupon = coupon

#         # Prepare the context to be passed to the template
#         context = {
#             'quantity': quantity,
#             'total': total,
#             'cart_items': cart_items,
#             'grand_total': grand_total,
#             'coupons': coupons,
#             'available_coupons': available_coupons,
#             'selected_coupon': selected_coupon
#         }

#         # Render the cart page with the context
#         return render(request, 'cart/cart.html', context)

#     except Exception as e:
        
#         return render(request,'error_404.html')


def add_cart_item(request, product_id):
    try:
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

            except ProductVariant.DoesNotExist as e:
                messages.error(request, 'Invalid Size')
                logging.error(f"Error in add_cart_item: {e}")
                return redirect('product_details', product_id)

        if variant.stock <= 0:
            messages.error(request, "This variant is out of stock.")
            return redirect('product_details', product_id)

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_cart_id(request))
            cart.save()

        try:
            if 'user' in request.session:
                my_user = request.user
                cart_item = CartItem.objects.get(product=variant, customer=my_user)
                if variant.stock > cart_item.quantity:
                    cart_item.quantity += 1
                else:
                    messages.error(request, "Only one piece is left")
            else:
                cart_item = CartItem.objects.get(product=variant, cart=cart)
                if variant.stock > cart_item.quantity:
                    cart_item.quantity += 1
                else:
                    messages.error(request, "Only one piece is left")

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

    except Exception as e:
        
        return render(request,'error_404.html')


@cache_control(no_cache=True, no_store=True)
def add_cart_quantity(request, cart_item_id):
    try:
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
            messages.error(request, "Only one piece is left")

        return redirect('cart')

    except Exception as e:
        # Log the exception for further investigation
        logging.error(f"Error in add_cart_quantity view: {e}")
        # Return an error response or redirect to an error page
        return HttpResponse("An error occurred", status=500)
    

@cache_control(no_cache=True, no_store=True)
def remove_cart_quantity(request, cart_item_id):
    try:
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

    except Exception as e:
        # Log the exception for further investigation
        logging.error(f"Error in remove_cart_quantity view: {e}")
        # Return an error response or redirect to an error page
        return HttpResponse("An error occurred", status=500)


@cache_control(no_cache=True, no_store=True)
def delete_cart_item(request, variant_id):
    try:
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

    except Exception as e:
        # Log the exception for further investigation
        logging.error(f"Error in delete_cart_item view: {e}")
        # Return an error response or redirect to an error page
        return HttpResponse("An error occurred", status=500)


@cache_control(no_cache=True, no_store=True)
def clear_cart(request):
    try:
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

    except Exception as e:
        # Log the exception for further investigation
        logging.error(f"Error in clear_cart view: {e}")
        # Return an error response or redirect to an error page
        return HttpResponse("An error occurred", status=500)


def clear_coupon(request):
    try:
        if 'selected_coupon_code' in request.session:
            del request.session['selected_coupon_code']

        if 'grand_total' in request.session:
            del request.session['grand_total']

        return redirect('cart')

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        print(e)
        return HttpResponse("An error occurred", status=500)


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def checkout(request):
    try:
        # Check if the user is an admin
        if 'email' in request.session:
            return redirect('admin_dashboard') 
    
        if 'user' in request.session:
            my_user = request.user
            cart_items = CartItem.objects.filter(customer=my_user)

            # Redirect to index if the cart is empty
            if not cart_items:
                return redirect('index')

            try:
                # Retrieve user's addresses
                addresses = UserAddress.objects.filter(user=my_user)
            except Exception as e:
                # Log the exception or handle it as needed
                print(e)
                messages.error(request, "Choose an address")
                return redirect('checkout')

            # Initialize total and grand_total
            total = Decimal(0)
            grand_total = Decimal(0)

            # Calculate total and grand_total from cart items
            for item in cart_items:
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
                    return redirect('checkout')  # Redirect back to prevent processing with an invalid coupon
            else:
                # No coupon selected, set coupon to None
                coupon = None

            if request.method == 'POST':
                try:
                    # Retrieve the selected delivery address
                    delivery_address = UserAddress.objects.get(id=request.POST['delivery_address'])
                except UserAddress.DoesNotExist:
                    messages.error(request, "Please choose a delivery address.")
                    return redirect('checkout')

                # Store the selected address ID in the session
                request.session['selected_address_id'] = delivery_address.id

                # Retrieve the selected payment method
                payment_method = request.POST.get('payment_method')

                # If no payment method is selected, set an error message
                if not payment_method:
                    messages.error(request, "Please select a payment method.")
                    return redirect('checkout')

                if payment_method == "razorpayPayment":
                    # Redirect to the online payment page
                    return redirect('online_payment')

                elif payment_method == "cash_on_delivery":
                    # Process cash on delivery payment

                    # Check if the 'remove_coupon' field is present in the form
                    if 'remove_coupon' in request.POST:
                        # If the user chooses to remove the coupon
                        if 'selected_coupon_code' in request.session:
                            del request.session['selected_coupon_code']  # Remove the coupon code from the session
                            # Recalculate the grand total without the coupon discount
                            grand_total = Decimal(0)
                            for item in cart_items:
                                grand_total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)

                    total = grand_total

                    # Create a payment record
                    payment = Payments.objects.create(
                        user=my_user,
                        payment_method=payment_method,
                        total_amount=grand_total,
                    )
                    payment.save()

                    # Create an order record
                    order = Order.objects.create(
                        user=my_user, 
                        address=delivery_address,
                        payment=payment,
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

                    # Create order items and update variant stock
                    cart_items = CartItem.objects.filter(customer=my_user)
                    for item in cart_items:
                        variant = ProductVariant.objects.get(id=item.product.id)
                        order_item = OrderProduct.objects.create(
                            customer=my_user,
                            order_id=order,
                            payment_id=payment.id,
                            variant=variant,
                            quantity=item.quantity,
                            product_price=variant.product.selling_price,
                            ordered=True,
                        )
                        variant.stock -= item.quantity
                        variant.save()
                        item.delete()

                    # Redirect to the order confirmed page
                    return redirect('order_confirmed', order_id)
                       
                elif payment_method == "walletPayment":
                    try:
                        # Assuming 'wallet' is the field in your user model representing the wallet balance
                        wallet_amount = my_user.wallet

                        # Initialize total and grand_total
                        total = Decimal(0)
                        grand_total = Decimal(0)

                        # Calculate total and grand_total from cart items
                        for item in cart_items:
                            if item.product.product.category.offer:
                                offer_percentage = item.product.product.category.offer
                                discounted_price = item.product.product.selling_price - (
                                    item.product.product.selling_price * offer_percentage / 100
                                )
                                total += Decimal(discounted_price) * Decimal(item.quantity)
                            else:
                                total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)

                        grand_total = total

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
                                return redirect('checkout')  # Redirect back to prevent processing with an invalid coupon
                        else:
                            # No coupon selected, set coupon to None
                            coupon = None

                        # Check if the user has sufficient balance in the wallet
                        if wallet_amount >= grand_total:
                            # Deduct the amount from the wallet
                            my_user.wallet -= grand_total
                            my_user.save()

                            # Create a payment record
                            payment = Payments.objects.create(
                                user=my_user,
                                payment_method=payment_method,
                                total_amount=grand_total,
                            )
                            payment.save()

                            # Create an order record
                            order = Order.objects.create(
                                user=my_user,
                                address=delivery_address,
                                payment=payment,
                                total=total,
                                order_total=grand_total,
                            )
                            if coupon is not None:
                                order.coupon = coupon
                                del request.session['selected_coupon_code']
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

                            # Create order items and update variant stock
                            cart_items = CartItem.objects.filter(customer=my_user)
                            for item in cart_items:
                                variant = ProductVariant.objects.get(id=item.product.id)
                                order_item = OrderProduct.objects.create(
                                    customer=my_user,
                                    order_id=order,
                                    payment_id=payment.id,
                                    variant=variant,
                                    quantity=item.quantity,
                                    product_price=variant.product.selling_price,
                                    ordered=True,
                                )
                                variant.stock -= item.quantity
                                variant.save()
                                item.delete()

                            # Redirect to the order confirmed page
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
                'addresses': addresses,
                'cart_items' : cart_items,
                'grand_total' : grand_total,
                'selected_coupon_code': selected_coupon_code, 
                'applied_coupon': coupon,
            }

            # Render the checkout template with the context
            return render(request, "cart/checkout.html", context)

    except Exception as e:
    # Log the exception or handle it as needed
        print(e)
        messages.error(request, "Please select both address and payment method to place an order.")
        return redirect('checkout')