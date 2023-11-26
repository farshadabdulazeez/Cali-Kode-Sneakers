import datetime
from decimal import Decimal
from cart_app.models import *
from order.models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control


@cache_control(no_cache=True, no_store=True)
@login_required(login_url='index')
def order(request):
    context = {}
    try:
        # Get the user and their cart items
        user = request.user
        cart_items = CartItem.objects.filter(customer=user)
        
        # Redirect to index if there are no cart items
        if not cart_items:
            return redirect('index')

        context = {
            'cart_items': cart_items,
        }
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        
    # Render the order_confirmed.html template with the provided context
    return render(request, 'order/order_confirmed.html', context)


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def proceed_to_pay(request):
    try:
        # Get the total amount from the GET parameters
        total_amount = request.GET.get("grand_total")

        # Get the user and their cart items
        user = request.user
        cart = CartItem.objects.filter(customer=user)

        # Return the total amount as a JSON response
        return JsonResponse({
            'total_amount': total_amount,
        })
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        return JsonResponse({
            'error': 'An error occurred',
        })


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def online_payment(request):
    try:
        # Check if the user is logged in
        if 'user' in request.session:
            my_user = request.user
            cart_items = CartItem.objects.filter(customer=my_user)

        # Redirect to index if the cart is empty
        if not cart_items.exists():
            return redirect('index')
        
        total = 0
        grand_total = 0

        selected_address_id = request.session.get('selected_address_id')

        selected_address = UserAddress.objects.get(id=selected_address_id)

        cart_items = CartItem.objects.filter(customer=my_user).order_by('id')

        # Calculate the grand total considering category offers
        for item in cart_items:
            if item.product.product.category.offer:
                offer_percentage = item.product.product.category.offer
                discounted_price = item.product.product.selling_price - (
                    item.product.product.selling_price * offer_percentage / 100
                )
                grand_total += Decimal(discounted_price) * Decimal(item.quantity)
            else:
                grand_total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)

        # Fetch the stored coupon code from the session
        selected_coupon_code = request.session.get('selected_coupon_code')
        coupon_discount = 0

        # Apply coupon discount if a valid coupon is found
        if selected_coupon_code:
            try:
                selected_coupon = Coupons.objects.get(coupon_code=selected_coupon_code)
                coupon_discount = selected_coupon.discount
            except Coupons.DoesNotExist:
                messages.error(request, "Selected coupon not valid")
                del request.session['selected_coupon_code']  # Clear invalid coupon from session
                return redirect('checkout') 

        grand_total -= coupon_discount  # Subtract coupon discount after applying category offers

        # Handle POST request for payment confirmation
        if request.method == 'POST':
            address_id = request.POST.get('address_id')
            payment_method = request.POST.get('payment_method')
            payment_id = request.POST.get('payment_id')
            
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")

            # Create the payment object
            payment = Payments.objects.create(
                user=my_user,
                payment_method="Razorpay",
                total_amount=grand_total,
                status="Order confirmed",
            )
            payment.save()

            # Create the order object
            order = Order.objects.create(
                user=my_user,
                address=selected_address,
                payment=payment,
                total=total,
                order_total=grand_total
            )

            order_id = current_date + str(order.id)  # creating order id
            order.order_id = order_id
            order.save()

            # Update stock, clear cart, and finalize the order
            cart_items = CartItem.objects.filter(customer=my_user)
            for item in cart_items:
                variant = ProductVariant.objects.get(id=item.product.id)
                order_item = OrderProduct.objects.create(
                    customer=my_user,
                    order_id=order,
                    payment=payment,
                    variant=variant,
                    quantity=item.quantity,
                    product_price=item.product.product.selling_price,
                    ordered=True,
                )
                variant.stock -= item.quantity
                variant.save()
                item.delete()

            if payment_method == "Razorpay":
                order.is_ordered = True  # Set is_ordered to True after a successful order placement
                order.save()
                return JsonResponse(
                {
                    "status": "Your order has been placed successfully!",
                    "order_id": order_id,
                }
                )

        context = {
            'selected_address' : selected_address,
            'grand_total' : grand_total,
        }

        return render(request, 'order/online_payment.html', context)
    
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        return JsonResponse({
            'error': 'An error occurred',
        })


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_confirmed(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order_products = OrderProduct.objects.filter(order_id=order)

        context = {
            "order": order,
            "order_products": order_products,
        }
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('index')  # Redirect to the appropriate page when the order is not found
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "Error!")
        return redirect('checkout')

    messages.success(request,"Order has been placed successfully")
    return render(request, "order/order_confirmed.html", context)


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_confirmed_online(request):

    return render(request, 'order/order_confirmed_online.html')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_page_add_address(request, id):
    try:
        # Check if the user is logged in
        if 'user' in request.session:
            user = request.user
            
        # Handle POST request for adding a new address
        if request.method == 'POST':
            name = request.POST['name']
            mobile = request.POST['mobile']
            address = request.POST['address']
            city = request.POST['city']
            landmark = request.POST['landmark']
            pincode = request.POST['pincode']
            district = request.POST['district']
            state = request.POST['state']

            # Use the user's first name if 'name' is not provided
            if not name:
                name = user.first_name

            # Check if the mobile number is 10 characters long
            if len(mobile) == 10:
                user_address = UserAddress(
                    user=user,
                    name=name,
                    mobile=mobile,
                    address=address,
                    city=city,
                    landmark=landmark,
                    pincode=pincode,
                    district=district,
                    state=state
                )
                user_address.save()
                messages.success(request, "Address successfully created!")

            else:
                messages.error(request, "Mobile number must be 10 characters long!")

        return redirect('checkout')
    
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "An error occurred while adding the address.")
        return redirect('checkout')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_page_edit_address(request, id):
    try:
        # Check if the user is logged in
        if 'user' in request.session:
            user = request.user

        # Handle POST request for editing an existing address
        if request.method == 'POST':
            name = request.POST['name']
            mobile = request.POST['mobile']
            address = request.POST['address']
            city = request.POST['city']
            landmark = request.POST['landmark']
            pincode = request.POST['pincode']
            district = request.POST['district']
            state = request.POST['state']

            # Use the user's first name if 'name' is not provided
            if not name:
                name = user.first_name

            # Check if the mobile number is 10 characters long
            if len(mobile) == 10:
                try:
                    # Get the user's address by ID
                    user_address = UserAddress.objects.get(id=id, user=user)

                    # Update the user's address with the new data
                    user_address.name = name
                    user_address.mobile = mobile
                    user_address.address = address
                    user_address.city = city
                    user_address.landmark = landmark
                    user_address.pincode = pincode
                    user_address.district = district
                    user_address.state = state

                    user_address.save()
                    messages.success(request, "Address successfully updated!")

                except UserAddress.DoesNotExist:
                    messages.error(request, "Address not found or you don't have permission to edit this address.")
            else:
                messages.error(request, "Mobile number must be 10 characters long!")

        return redirect('checkout')

    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "An error occurred while updating the address.")
        return redirect('checkout')

