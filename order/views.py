from cart_app.models import *
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
    checkout_items = Checkout.objects.get(user=user)
    cart_items = CartItem.objects.filter(customer=user)
    
    if not cart_items:
        return redirect('index')

    context = {
        'checkout_items': checkout_items,
        'cart_items': cart_items,
    }
    # except Exception as e:
    #     print(e)
    return render(request, 'order/order_confirmed.html', context)


def online_payment(request):

    my_user = request.user
    total = 0
    grand_total = 0

    selected_address_id = request.session.get('selected_address_id')

    selected_address = UserAddress.objects.get(id=selected_address_id)

    cart_items = CartItem.objects.filter(customer=my_user).order_by('id')

    for item in cart_items:
        total = total + (float(item.product.product.selling_price) * float(item.quantity))
    grand_total = total   

    payment_method = request.POST.get('payment_method')

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


