import datetime
from decimal import Decimal
from cart_app.models import *
from order.models import *
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

# Create your views here.

@cache_control(no_cache=True, no_store=True)
@login_required(login_url='index')
def order(request):

    context = {}
    try:
        user = request.user
        cart_items = CartItem.objects.filter(customer=user)
        
        if not cart_items:
            return redirect('index')

        context = {
            'cart_items': cart_items,
        }
    except Exception as e:
        print(e)
    return render(request, 'order/order_confirmed.html', context)


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def proceed_to_pay(request):

    total_amount = 0
    total_amount = request.GET.get("grand_total")

    user = request.user
    cart = CartItem.objects.filter(customer=user)

    return JsonResponse({
        'total_amount' : total_amount,
    })


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def online_payment(request):

    my_user = request.user
    total = 0
    grand_total = 0

    selected_address_id = request.session.get('selected_address_id')

    selected_address = UserAddress.objects.get(id=selected_address_id)

    cart_items = CartItem.objects.filter(customer=my_user).order_by('id')

    # for item in cart_items:
    #     grand_total += Decimal(item.product.product.selling_price) * Decimal(item.quantity)

    # # Fetch the stored coupon code from the session
    # selected_coupon_code = request.session.get('selected_coupon_code')
    # if selected_coupon_code:
    #     try:
    #         selected_coupon = Coupons.objects.get(coupon_code=selected_coupon_code)
    #         grand_total -= selected_coupon.discount
    #     except Coupons.DoesNotExist:
    #         messages.error(request, "Selected coupon not valid")
    #         del request.session['selected_coupon_code']  # Clear invalid coupon from session
    #         return redirect('checkout')
    for item in cart_items:
        # Check if the product has a category offer
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

    if selected_coupon_code:
        try:
            selected_coupon = Coupons.objects.get(coupon_code=selected_coupon_code)
            coupon_discount = selected_coupon.discount
        except Coupons.DoesNotExist:
            messages.error(request, "Selected coupon not valid")
            del request.session['selected_coupon_code']  # Clear invalid coupon from session
            return redirect('checkout') 

    grand_total -= coupon_discount  # Subtract coupon discount after applying category offers
 


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
            variant.stock -= variant.stock - item.quantity
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


# def order_confirmed(request, order_id=None):

#     # if order_id is None:
#     #     order_id = "2038473462134"
#     context = {
#         "order_number":order_id
#     }
#     return render(request, "order/order_confirmed.html", context)

def order_confirmed(request, order_id=None):
    order = get_object_or_404(Order, order_id=order_id)
    order_products = OrderProduct.objects.filter(order_id=order)

    context = {
        "order": order,
        "order_products": order_products,
    }

    return render(request, "order/order_confirmed.html", context)


def order_confirmed_online(request):

    return render(request, 'order/order_confirmed_online.html')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_page_add_address(request, id):

    if 'email' in request.session:
        return redirect('admin_dashboard')
    
    if 'user' in request.session:
        user = request.user
        
    if request.method == 'POST':
        name = request.POST['name']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        landmark = request.POST['landmark']
        pincode = request.POST['pincode']
        district = request.POST['district']
        state = request.POST['state']

        if not name:
            name = user.first_name

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


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_page_edit_address(request, id):
    if 'email' in request.session:
        return redirect('admin_dashboard')

    if 'user' in request.session:
        user = request.user

    if request.method == 'POST':
        name = request.POST['name']
        mobile = request.POST['mobile']
        address = request.POST['address']
        city = request.POST['city']
        landmark = request.POST['landmark']
        pincode = request.POST['pincode']
        district = request.POST['district']
        state = request.POST['state']

        if not name:
            name = user.first_name

        if len(mobile) == 10:
            try:
                user_address = UserAddress.objects.get(id=id, user=user)
                
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



