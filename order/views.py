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


def order_confirmed(request):

    return render (request, 'order/order_confirmed.html')


