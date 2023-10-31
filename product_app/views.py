from django.http import HttpResponse
from django.shortcuts import redirect, render
from product_app.models import *
from user_app.models import *
from django.db.models import Q


def products(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')

    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(category__in=categories, is_available=True)

    context = {
        'products' : products,
        'product_count': products.count(),
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
        'product_id' : product_id,
        'variant': variant,
        'products': all_products,
        'multiple_images': multiple_images,
        'user_id': user_id,
    }

    return render(request, 'product/product_details.html', context)


def product_search(request):

    search_query = request.GET.get('search', '')
    categories = Category.objects.filter(is_active=True)
    
    if search_query:
        products = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(brand__brand_name__icontains=search_query) |
            Q(category__category_name__iexact=search_query)  # Check for an exact match with the category name
        ).filter(category__in=categories, is_available=True)
    else:
        products = Product.objects.filter(category__in=categories, is_available=True)


    context = {
        'products': products,
        'search_query': search_query,
    }

    return render(request, 'product/products.html', context)