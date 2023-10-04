from django.http import HttpResponse
from django.shortcuts import render
from product_app.models import *
from user_app.models import *



def products(request):

    products = Product.objects.filter(is_available=True)

    context = {
        'products' : products,
    }
    
    return render(request, 'product/products.html', context)


def product_details(request, id):

    products = Product.objects.all()
    single_product = Product.objects.get(id=id)
    
    current_user = request.user
    user_id = current_user.id
    product_id = single_product.id
    all_products = Product.objects.all()
    variant = ProductVariant.objects.filter(product=product_id)
    multiple_images = MultipleImages.objects.filter(product=product_id).order_by('-id')

    context = {
        'product': single_product,
        'variant': variant,
        'products': all_products,
        'multiple_images': multiple_images,
        'user_id': user_id,
    }

    return render(request, 'product/product_details.html', context)




