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

    selected_brands = request.GET.getlist('brand')
    selected_sizes = request.GET.getlist('size')
    selected_categories = request.GET.getlist('category')
    price = request.GET.get('price')

    if selected_brands:
        products = products.filter(brand__brand_name__in=selected_brands)

    if selected_sizes:
        products = products.filter(productvariant__product_size__size__in=selected_sizes)

    if selected_categories:
        products = products.filter(category__category_name__in=selected_categories)

    if price:
        price_values = price.split('-')
        if len(price_values) == 2:
            min_price = price_values[0] if price_values[0] else 0
            max_price = price_values[1] if price_values[1] else 9999999  # Or any sufficiently high value
            products = products.filter(selling_price__gte=min_price, selling_price__lte=max_price)
        else:
            return HttpResponse("Invalid price range format. Please use 'min-max' format.", status=400)

    product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        'selected_brands': selected_brands,
        'selected_sizes': selected_sizes,
        'selected_categories': selected_categories,
        'price_range': price,
        'categories': categories,
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