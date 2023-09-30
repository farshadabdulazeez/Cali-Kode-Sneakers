from django.shortcuts import render


def products(request):
    
    return render(request, 'product/products.html')


def product_details(request):

    return render(request, 'product_details.html')