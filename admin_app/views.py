import os

from django.forms import ValidationError
from order.models import *
from decimal import Decimal
from user_app.models import *
from product_app.models import *
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required


@cache_control(no_cache=True, no_store=True)
def admin_login(request):  
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        admin = authenticate(email=email, password=password)
        
        if admin:
            if admin.is_superuser:
                login(request, admin)
                request.session['email'] = email
                return redirect('admin_users')
            else:
                messages.error(request, "You can't access this session with user credentials.")
        else:
            messages.error(request, "Invalid credentials, try again with valid credentials.")
    return render(request, 'admin/admin_login.html')


@staff_member_required(login_url='admin_login')
def admin_dashboard(request):

    return render(request, 'admin/admin_dashboard.html')


@staff_member_required(login_url='admin_login')
def admin_users(request):

    context = {}
    try:
        users = CustomUser.objects.all().order_by('id')
        context = {
            'users' : users,
        }
    except Exception as e:
        print(e)

    return render(request, 'admin/admin_users.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_users_control(request, id):

    try:
        user = CustomUser.objects.get(id=id)
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
    except Exception as e:
        print(e)

    return redirect('admin_users')


@staff_member_required(login_url='admin_login')
def admin_category(request):

    context = {}
    try:
        categories = Category.objects.all().order_by('id')
        context = {
            'categories': categories
        }
    except Exception as e:
        print(e)

    return render(request, 'admin/admin_category.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_category(request):

    try:
        if request.method == 'POST':
            category_name = request.POST['category_name']
            category_slug = category_name.replace("-"," ")
            existing_category = Category.objects.filter(category_name__iexact=category_name)
           
            if existing_category.exists():
                messages.error(request, 'Category exists!')
                return redirect('admin_add_category')
            
            category = Category(
                category_name = category_name,
                category_description = request.POST['category_description'],
                slug= category_slug,
                offer=request.POST.get('category_offer')
            )

            if request.FILES:
                category.category_image = request.FILES['category_image']

            category.save()
            messages.success(request, 'Category added!')
            return redirect('admin_category')
        
    except Exception as e:
        print(e)

    return render(request, 'admin/admin_add_category.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_category(request, id):

    try:
        category = Category.objects.get(id=id)

        context = {
            'category': category,
        }

        if request.method == 'POST':
            if 'category_image' in request.FILES:
                if category.category_image:
                    os.remove(category.category_image.path)
                category.category_image = request.FILES['category_image']
            category.category_name = request.POST['category_name']
            category.category_description = request.POST['category_description']
            # Check if offer field exists in the form submission
            if 'category_offer' in request.POST:
                category_offer = int(request.POST['category_offer'])
                category.offer = category_offer
                
            category.save()

            messages.success(request, "Category Updated!")
            return redirect('admin_category')
        
        return render(request, 'admin/admin_edit_category.html', context)
    
    except Exception as e:
        print(e)

        return redirect('admin_category')

    
# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_delete_category(request, id):

#     try:
#         category = Category.objects.get(id=id)
#         if category.category_image:
#             os.remove(category.category_image.path)
#         category.delete()
#         messages.success(request, "Category Deleted!")

#     except Exception as e:
#         print(e)

#     return redirect('admin_category')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_control_category(request, id):

    try:
        category = Category.objects.get(id=id)
        if category.is_active:
            category.is_active = False
            category.save()
            messages.success(request, "Category unlisted!")
        else:
            category.is_active = True
            category.save()
            messages.success(request, "Category listed!")

    except Exception as e:
        print(e)

    return redirect('admin_category')


@staff_member_required(login_url='admin_login')
def admin_brands(request):

    context = {}

    brands = ProductBrand.objects.all()
    context = {
        'brands' : brands
    }

    return render(request, 'admin/admin_brands.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_brand(request):
    if request.method == 'POST':
        brand_name = request.POST['brand_name']
        brand_description = request.POST['brand_description']

        # Check if a brand with the same name already exists
        existing_brand = ProductBrand.objects.filter(brand_name=brand_name).first()

        if existing_brand:
            # Update the existing brand's description and image if provided
            existing_brand.brand_description = brand_description
            
            if request.FILES:
                existing_brand.brand_image = request.FILES['brand_image']
                
            existing_brand.save()
            
            messages.success(request, "Brand updated successfully!")
        else:
            # Create a new brand only if it doesn't exist
            brand = ProductBrand(
                brand_name=brand_name,
                brand_description=brand_description,
            )
            
            if request.FILES:
                brand.brand_image = request.FILES['brand_image']

            brand.save()
            messages.success(request, "Brand added successfully!")

        return redirect('admin_brands')

    return render(request, 'admin/admin_add_brand.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_brand(request, id):
    try:
        brand = ProductBrand.objects.get(id=id)

        if request.method == 'POST':
            brand_name = request.POST['brand_name']
            brand.brand_name = brand_name
            slug = brand_name.replace("-", " ")
            brand.slug = slug
            brand.brand_description = request.POST['brand_description']

            if 'brand_image' in request.FILES:
                if brand.brand_image:
                    os.remove(brand.brand_image.path)
                brand.brand_image = request.FILES['brand_image']

            brand.save()
            messages.success(request, "Brand updated")
            return redirect('admin_brand')

        context = {
            'brand': brand,
        }

        return render(request, 'admin/admin_edit_brand.html', context)
    
    except Exception as e:
        print(e)
        return redirect('admin_brands')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_brand(request, id):
    try:
        brand = ProductBrand.objects.get(id=id)
        if brand:
            brand.delete()
            messages.success(request, "Brand deleted successfully!")
            return redirect('admin_brands')
    except ProductBrand.DoesNotExist:
        messages.error(request, "Brand does not exist.")
        return redirect('admin_brands')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_control_brand(request, id):
    try:
        brand = ProductBrand.objects.get(id=id)
        if brand.is_active:
            brand.is_active = False
            messages.success(request, "Brand unlisted!")
        else:
            brand.is_active = True
            messages.success(request, "Brand listed!")
        brand.save()
    except ProductBrand.DoesNotExist:
        messages.error(request, "Brand not found.")
    except Exception as e:
        print(e)
        messages.error(request, "An error occurred.")

    return redirect('admin_brands')



@staff_member_required(login_url='admin_login')
def admin_products(request):

    context = {}

    try:
        products = Product.objects.all()
        context = {
            'products' : products
        }

    except Exception as e:
        print(e)

    return render(request, 'admin/admin_products.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_product(request):

    categories = Category.objects.all()
    brands = ProductBrand.objects.all()

    context = {
        'categories': categories,
        'brands': brands,
    }

    try:
        if request.method == 'POST':
            product = Product()
            category = request.POST['category']
            brand = request.POST['brand']
            original_price = int(request.POST['original_price'])
            selling_price = int(request.POST['selling_price'])
            product_offer = int(request.POST['product_offer'])

            # single image fetching
            try:
                product_image = request.FILES.get('product_image', None)
                if product_image:
                    product.product_image = product_image

            except Exception as e:
                print(e)

            product_name = request.POST['product_name']
            product.product_name = product_name
            product_slug = product_name.replace(" ", "-")
            product.slug = product_slug
            product.category = Category.objects.get(id=category)
            product.brand = ProductBrand.objects.get(id=brand)
            product.original_price = original_price

            if product_offer > 0 :
                offer_amount = (original_price * product_offer)//100
                if (original_price - offer_amount) < selling_price : 
                    selling_price = original_price - offer_amount
                    
            product.selling_price = selling_price
            product.product_description = request.POST['product_description']
            product.save()

            # multiple image fetching
            try:
                multiple_images = request.FILES.getlist('multiple_images', None)
                if multiple_images:
                    for image in multiple_images:
                        photo = MultipleImages.objects.create(
                            product=product,
                            images=image,
                        )
                        photo.save()
            except Exception as e:
                print(e)

            messages.success(request, "Product Created Successfully!")

            return redirect('admin_products')
        
    except Exception as e:
        messages.error(request, "Product is already exist!")
        print(e)

    return render(request, 'admin/admin_add_product.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_product(request, id):

    product = Product.objects.get(id=id)
    product_category = product.category
    product_brand = product.brand
    multiple_images = MultipleImages.objects.filter(product=id)
    brands = ProductBrand.objects.all()
    categories = Category.objects.all()

    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
        'product_category': product_category,
        'product_brand': product_brand,
        'multiple_images': multiple_images,
    }

    try:
        if request.method == 'POST':

            product_name = request.POST['product_name']
            category = request.POST['category']
            brand = request.POST['brand']
            original_price = float(request.POST.get('original_price'))
            selling_price = float(request.POST.get('selling_price'))
            product_offer = int(request.POST.get('product_offer'))

            if product_offer > 0:
                offer_amount = (original_price * product_offer) / 100
                # Calculate the new selling price based on the offer
                selling_price = original_price - offer_amount

            single_image = request.FILES.get('product_image', None)

            multiple_images = request.FILES.getlist('multiple_images')
            # we want to remove the image that already stored in the database.
            # first of all we have to check if there is any image exist on product object.
            if single_image:
                if product.product_image:
                    product.product_image.delete()
                product.product_image = single_image

            if multiple_images:
            # Clear existing multiple images for the product
                MultipleImages.objects.filter(product=product).delete()

                # Add new multiple images
                for image in multiple_images:
                    MultipleImages.objects.create(product=product, images=image)


            product.product_name = product_name
            product.category = Category.objects.get(id=category)
            product.brand = ProductBrand.objects.get(id=brand)
            product.original_price = original_price
            product.selling_price = selling_price

            product.save()
            messages.success(request, "Product updated successfully!")
            return redirect('admin_products')
    except Exception as e:
        print(e)

    return render(request, 'admin/admin_edit_product.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_product(request, id):

    product = Product.objects.get(id=id)
    if product.product_image:
        if len(product.product_image) != 0:
            os.remove(product.product_image.path)
    product.delete()
    messages.success(request, "Product deleted successfully!")

    return redirect('admin_products')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_control_product(request, id):

    try:
        product = Product.objects.get(id=id)
        if product.is_available:
            product.is_available = False
            messages.success(request, "Product unlisted!")
        else:
            product.is_available = True
            messages.success(request, "Product listed!")
        product.save()

    except Exception as e:
        print(e)
    return redirect('admin_products')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_product_variant(request, product_id):

    context = {}

    variant = ProductVariant.objects.filter(product=product_id)

    context = {
        'variants' : variant,
        'product_id' : product_id,
    }

    return render(request, 'admin/admin_product_variant.html',context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_product_variant(request,product_id):

    context = {}

    product = Product.objects.get(id=product_id)
    product_variants = ProductVariant.objects.filter(product=product)
    sizes = ProductSize.objects.all().order_by('id')

    if request.method == 'POST':
        size_id = request.POST['size']
        stock = request.POST['stock']
        variant_size = ProductSize.objects.get(id=size_id)

        try:
            variant = ProductVariant.objects.get(product=product_id, product_size=variant_size)

            if variant:
                print("Existing variant")
                variant.stock = variant.stock + int(stock)
        except:
            variant = ProductVariant.objects.create(
                product=product,
                product_size=variant_size,
                stock=stock,
            )
        return redirect('admin_product_variant', product_id)

    context = {
        'product': product,
        'sizes': sizes,
        'product_variants': product_variants,
    }
    return render(request, 'admin/admin_add_product_variant.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_product_variant(request):
    try:
        if request.method == 'POST':
            id = request.POST['id']
            stock = request.POST['stock']
            variant = ProductVariant.objects.get(id=id)
            product_id = variant.product
            variant.stock = stock
            variant.save()

        return redirect('admin_product_variant', product_id.id)
    
    except ProductVariant.DoesNotExist:
        pass

    except Exception as e:
        print(e)

    return redirect('admin_product_variant')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_product_variant(request, variant_id):

    try:
        variant = ProductVariant.objects.get(id=variant_id)
        product = variant.product
        
        if variant:
            variant.delete()
            
            return redirect('admin_product_variant', product.id)
        
    except Exception as e:
        print(e)

    return redirect('admin_dashboard')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_control_product_variant(request, variant_id):

    try:
        variant = ProductVariant.objects.get(id=variant_id)
        product_id = variant.product.id
        if variant.is_active:
            variant.is_active = False
        else:
            variant.is_active = True
        variant.save()
        return redirect('admin_product_variant', product_id)
    except Exception as e:
        print(e)
        return redirect('admin_products')
    

@staff_member_required(login_url='admin_login')
def admin_coupons(request):
    context = {}
    try:
        coupons = Coupons.objects.all().order_by('-id') 
        context = {
            'coupons': coupons,
        }
        return render(request, 'admin/admin_coupons.html', context)

    except Exception as e:
        print(e)
        return render(request, 'admin/admin_coupons.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_coupon(request):

    if request.method == "POST":

        try:
            coupon_code = request.POST.get("coupon_code", "").strip()
            discount = float(request.POST.get("discount", 0))
            minimum_order_amount = float(request.POST.get("minimum_order_amount", 0))
            valid_from = request.POST.get("valid_from", "")
            valid_to = request.POST.get("valid_to", "")
            description = request.POST.get("description", "") 

            if discount < 1:
                messages.error(request, "The minimum discount amount should be 1.")
            elif discount > minimum_order_amount:
                messages.error(request, "The discount must be less than the minimum order amount.")
            elif valid_from > valid_to:
                messages.error(request, "Please ensure the validity range is correct.")
            else:
                coupon = Coupons.objects.create(
                    coupon_code=coupon_code,
                    discount=discount,
                    minimum_order_amount=minimum_order_amount,
                    valid_from=valid_from,
                    valid_to=valid_to,
                    description=description 
                )
                coupon.save()
                messages.success(request, "New coupon added successfully.")
                return redirect("admin_coupons")

        except ValidationError as e:
            messages.error(request, f"Validation Error: {e}")
        except Exception as e:
            print(e) 

    return render(request, 'admin/admin_add_coupon.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_coupon(request, coupon_id):
    try:
        coupon = get_object_or_404(Coupons, id=coupon_id)

        if request.method == "POST":

            coupon_code = request.POST.get("coupon_code", "").strip()
            new_discount = request.POST.get("discount", "0")

            discount = Decimal(new_discount)
            minimum_order_amount = int(request.POST.get("minimum_order_amount", "0"))

            if discount < 1:
                messages.error(request, "Minimum discount amount should be 1")
                return redirect("admin_coupons")

            if discount >= minimum_order_amount:
                messages.error(request, "Discount has to be less than minimum amount")
                return redirect("admin_coupons")

            valid_from = request.POST.get("valid_from", "")
            valid_to = request.POST.get("valid_to", "")

            if valid_from > valid_to:
                messages.error(request, "Add validity range properly")
                return redirect("admin_coupons")

            coupon.coupon_code = coupon_code
            coupon.discount = discount
            coupon.minimum_order_amount = minimum_order_amount
            coupon.valid_from = valid_from
            coupon.valid_to = valid_to
            coupon.save()
            messages.success(request, "Coupon updated successfully!")
            return redirect("admin_coupons")


    except Coupons.DoesNotExist:
        messages.error(request, "Coupon not found")
        return redirect("admin_coupons")
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return render(request, 'admin/admin_edit_coupon.html')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_coupon(request, coupon_id):
    try:
        coupon = get_object_or_404(Coupons, id=coupon_id)
        coupon.delete()
        messages.success(request, "Coupon deleted succcessfully")
    except Coupons.DoesNotExist as e:
        messages.error(request, "Coupon not found")
    except Exception as e:
        messages.error(request, "An error occurred while deleting the coupon")
    return redirect('admin_coupons')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_activate_coupon(request, coupon_id):
    try:
        coupon = Coupons.objects.get(id=coupon_id)
        if coupon.active:
            coupon.active = False
            messages.success(request, "Coupon deactivated")
        else:
            coupon.active = True
            messages.success(request, "Coupon activated")
        coupon.save()
    except Exception as e:
        print(e)
    return redirect('admin_coupons')


@staff_member_required(login_url='admin_login')
def admin_orders(request):
    context = {}
    # try:
    orders = Order.objects.all().order_by('-order_id')
    context = {
        'orders': orders,
    }
    # except Exception as e:
    #     print(e)
    return render(request, 'admin/admin_orders.html', context)


@staff_member_required(login_url="admin_login")
def admin_orders_detail(request, id):

    order = Order.objects.get(id=id)
    
    order_items = OrderProduct.objects.filter(order_id=order)
    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "admin/admin_orders_detail.html", context)


@staff_member_required(login_url="admin_login")
def admin_orders_status(request, id):

    if request.method == 'POST':

        new_status = request.POST.get('new_status')
        order = Order.objects.get(id=id)
        order.status = new_status
        order.save()

    return redirect('admin_orders')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    request.session.flush()
    return redirect('admin_login')
