import datetime
from decimal import Decimal
from cart_app.models import *
from order.models import *
from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

# Create your views here.

@cache_control(no_cache=True, no_store=True)
@login_required(login_url='index')
def order(request):

    context = {}
    # try:
    user = request.user
    # checkout_items = Checkout.objects.get(user=user)
    cart_items = CartItem.objects.filter(customer=user)
    
    if not cart_items:
        return redirect('index')

    context = {
        # 'checkout_items': checkout_items,
        'cart_items': cart_items,
    }
    # except Exception as e:
    #     print(e)
    return render(request, 'order/order_confirmed.html', context)


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def proceed_to_pay(request):

    cart = request.GET.get("grand_total")

    user = request.user
    cart = CartItem.objects.filter(customer=user)

    total_amount = 0   
    for item in cart:
        total_amount = total_amount + item.product.product.selling_price * item.quantity
    print(total_amount)

    return JsonResponse({
        'total_amount' : total_amount,
    })



def online_payment(request):
    print("--------1--------")

    my_user = request.user
    total = 0
    grand_total = 0

    selected_address_id = request.session.get('selected_address_id')
    print("---------2-------")

    selected_address = UserAddress.objects.get(id=selected_address_id)
    print("---------3-------")
    

    cart_items = CartItem.objects.filter(customer=my_user).order_by('id')
    print("---------4------")

    for item in cart_items:
        total = total + (float(item.product.product.selling_price) * float(item.quantity))
    grand_total = total   
    print("--------5-------")


    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method')
        payment_id = request.POST.get('payment_id')
        print("-----------6-----------")

        
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr, mt, dt)
        current_date = d.strftime("%Y%m%d")
        print("-----------7-----------")


        # Create the payment object
        payment = Payments.objects.create(
            user=my_user,
            payment_method="Razorpay",
            total_amount=grand_total,
            status="Order confirmed",
        )
        payment.save()
        print("-----------8-----------")

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
        print("-----------9-----------")


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
            variant.stock = variant.stock - item.quantity
            variant.save()
            item.delete()
            print("-----------10-----------")

        if payment_method == "Razorpay":
            order.is_ordered = True  # Set is_ordered to True after a successful order placement
            order.save()
            print('---------------45-----------------')
            return JsonResponse(
            {
                "status": "Your order has been placed successfully!",
                "order_id": order_id,
            }
            )

    #     return redirect('order_confirmed')

    context = {
        'selected_address' : selected_address,
        'grand_total' : grand_total,
    }

    return render(request, 'order/online_payment.html', context)


def order_confirmed(request):

    return render (request, 'order/order_confirmed.html')


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


