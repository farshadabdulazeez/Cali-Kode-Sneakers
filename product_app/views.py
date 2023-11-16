from decimal import Decimal
from django.http import HttpResponse
from django.shortcuts import redirect, render
from product_app.models import *
from user_app.models import *
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def products(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')

    categories = Category.objects.filter(is_active=True)
    products_all = Product.objects.filter(category__in=categories, is_available=True)
    sizes = ProductSize.objects.all()

    selected_brands = request.GET.getlist('brand')
    selected_sizes = request.GET.getlist('size')
    selected_categories = request.GET.getlist('category')
    price = request.GET.get('price')

    if selected_brands:
        products_all = products_all.filter(brand__brand_name__in=selected_brands)

    if selected_sizes:
        products_all = products_all.filter(productvariant__product_size__size__in=selected_sizes)

    if selected_categories:
        products_all = products_all.filter(category__category_name__in=selected_categories)

    if price:
        price_values = price.split('-')
        if len(price_values) == 2:
            min_price = price_values[0] if price_values[0] else 0
            max_price = price_values[1] if price_values[1] else 9999999  # Or any sufficiently high value
            products_all = products_all.filter(selling_price__gte=min_price, selling_price__lte=max_price)
        else:
            return HttpResponse("Invalid price range format. Please use 'min-max' format.", status=400)

    product_count = products_all.count()

    for product in products_all:
        if product.category.offer:
            offer_percentage = product.category.offer
            new_selling_price = product.original_price - (product.original_price * offer_percentage / 100)
            product.selling_price = new_selling_price
        product.percentage_discount = calculate_percentage_discount(product.selling_price, product.original_price)

    # Number of products per page
    products_per_page = 9

    # Create a Paginator instance
    paginator = Paginator(products_all, products_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the products for the requested page
        products_paged = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        products_paged = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, show the last page
        products_paged = paginator.page(paginator.num_pages)

    context = {
        'products': products_paged,
        'sizes': sizes,
        'product_count': product_count,
        'selected_brands': selected_brands,
        'selected_sizes': selected_sizes,
        'selected_categories': selected_categories,
        'price_range': price,
        'categories': categories,
    }

    return render(request, 'product/products.html', context)


def calculate_percentage_discount(selling_price, original_price):
    if original_price > 0:
        discount = ((original_price - selling_price) / original_price) * 100
        return Decimal(discount).quantize(Decimal('0'))


def product_details(request, id):

    products = Product.objects.all()
    single_product = Product.objects.get(id=id)
    
    current_user = request.user
    user_id = current_user.id
    product_id = single_product.id
    all_products = Product.objects.all()
    variant = ProductVariant.objects.filter(product=product_id)
    multiple_images = MultipleImages.objects.filter(product=product_id).order_by('-id')

    # Check if any variant has stock greater than 0
    if not any(variant.stock > 0 for variant in variant):
        # If no variant has stock, display an error message or redirect to another page
        messages.error(request, "This product is currently out of stock.")
        return redirect('home')

    if single_product.category.offer:
        offer_percentage = single_product.category.offer
        new_selling_price = single_product.original_price - (single_product.original_price * offer_percentage / 100)
        single_product.selling_price = new_selling_price
        

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

    # Perform the search query
    if search_query:
        products_all = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(brand__brand_name__icontains=search_query) |
            Q(category__category_name__iexact=search_query)
        ).filter(category__in=categories, is_available=True)
    else:
        products_all = Product.objects.filter(category__in=categories, is_available=True)

    # Get selected sizes
    selected_sizes = request.GET.getlist('size')
    selected_categories = request.GET.getlist('category')

    # Filter products by selected sizes
    if selected_sizes:
        products_all = products_all.filter(productvariant__product_size__size__in=selected_sizes)

    if selected_categories:
        products_all = products_all.filter(category__category_name__in=selected_categories)


    # Get the sizes for the sidebar
    sizes = ProductSize.objects.all()

    # Number of products per page
    products_per_page = 9

    # Create a Paginator instance
    paginator = Paginator(products_all, products_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get('page')

    try:
        # Get the products for the requested page
        products_paged = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, show the first page
        products_paged = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, show the last page
        products_paged = paginator.page(paginator.num_pages)

    context = {
        'products': products_paged,
        'search_query': search_query,
        'selected_sizes': selected_sizes,
        'selected_categories': selected_categories,
        'sizes': sizes,
        'categories': categories,
    }

    return render(request, 'product/products.html', context)
