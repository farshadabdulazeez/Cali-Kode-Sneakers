from cart_app.models import *
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

    cart_items = CartItem.objects.filter(customer=my_user).order_by('id')

    for item in cart_items:
        total = total + (float(item.product.product.selling_price) * float(item.quantity))
    grand_total = total   
    
    context = {
        'grand_total' : grand_total,
    }

    return render(request, 'order/online_payment.html', context)


def order_confirmed(request):

    return render (request, 'order/order_confirmed.html')

def proceed_to_pay(request):
    cart = CartItem.objects.filter(user = request.user)
    total_amount = 0
    for item in cart:
        total_amount = total_amount + item.product.product.selling_price * item.quantity

    return JsonResponse({
        'total_amount' : total_amount
    })


