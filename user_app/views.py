from .models import *
from order.models import *
from product_app.models import *
from decimal import Decimal
from django.urls import reverse_lazy
from django.contrib import auth
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render



def index(request):

    context = {}

    categories = Category.objects.all().order_by('id')
    products = Product.objects.all()

    context = {
        'categories' : categories,
        'products' : products
    }

    return render(request, 'user/index.html', context)


@cache_control(no_cache=True, no_store=True)
def register(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user_name = request.POST.get('username')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        existing_email = CustomUser.objects.filter(email=email)
        existing_mobile = CustomUser.objects.filter(mobile=mobile)

        if existing_email:
            messages.error(request, "Email is already existing!")
            return redirect('register')
        elif existing_mobile:
            messages.error(request, "Mobile is already existing!")
            return redirect('register')
        else:
            if password == confirm_password:
                user = CustomUser.objects.create_user(email, password=password, mobile=mobile, first_name=first_name)
                user_id = user.id
                otp = get_random_string(length=6, allowed_chars='1234567890')

                subject = 'Verify your account!'
                message = f'''You have requested a One-Time Password (OTP) for account verification.
Please use the following OTP to complete the verification process:

OTP: {otp}

Please enter this OTP in the appropriate field on our website to verify your account.

If you did not request this OTP or have any concerns about your account's security,
please contact our support team immediately.

Thank you for using Cali Kode Sneakers!
'''
                           
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail(subject, message, email_from, recipient_list)
            
                user.otp = otp
                user.save()
                return redirect('otp_verification', user_id)
            else:
                 messages.error(request, "Passwords do not match!")
                 return redirect('register')

    return render(request, 'user/register.html')



@cache_control(no_cache=True, no_store=True)
def user_login(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')

    else:
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            user = authenticate(request, username=email, password=password)

            if user:  
                request.session['user'] = email
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, "Invalid Credentials, Try again!")
                return redirect('user_login')
                       
    return render(request, 'user/user_login.html')


@cache_control(no_cache=True, no_store=True)
def otp_verification(request, user_id):
    if 'email' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        return redirect('index')
    
    user = CustomUser.objects.get(id=user_id)
    context = {
        'user': user,
    }
    if request.method == 'POST':
        otp = request.POST['otp']
        
        if len(otp) == 6:
            if otp == user.otp:
                user.is_verified = True
                user.otp = ''
                user.save()
                messages.success(request, "Account successfully verified, Login now.")
                return redirect('user_login')
            else:
                messages.error(request, 'Invalid OTP, Try again')
                return redirect('otp_verificaion', user.id)
        else:
            messages.error(request, 'Please enter a valid OTP....')
    
    return render(request, 'user/otp_verification.html', context)


# @cache_control(no_cache=True,no_store=True)
# def regenerate_otp(request):
#     try:
#         user = CustomUser.objects.get(id=id)
#         email = user.email
#         user.otp = ''
#         otp = get_random_string(length=6, allowed_chars='1234567890')

#         subject = 'Verify your account'
#         message = f'''You have requested a One-Time Password (OTP) for account verification.
# Please use the following OTP to complete the verification process:

# OTP: {otp}

# Please enter this OTP in the appropriate field on our website to verify your account.

# If you did not request this OTP or have any concerns about your account's security,
# please contact our support team immediately.

# Thank you for using Cali Kode Sneakers!
# '''
#         email_from = settings.EMAIL_HOST_USER
#         recipient_list = [email, ]
#         send_mail(subject, message, email_from, recipient_list)

#         user.otp = otp
#         user.save()
#         messages.success(request, "An OTP has been sent to your email for verification.")
#     except Exception as e:
#         print(e)

#     return render(request, 'otp_verification')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def user_logout(request):

    if 'email' in request.session:
        return redirect('admin_dashboard')
    if 'user' in request.session:
        logout(request)
        request.session.flush()
        messages.success(request, 'Logout successfully!')
    return redirect('index')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def user_profile(request):

    if 'email' in request.session:
        return redirect('admin_dashboard') 
    if 'user' in request.session:
        user = request.user

    context = {}

    address = UserAddress.objects.filter(user=user)
    order_product = OrderProduct.objects.filter(customer=user)

    context = {
        'address' : address,
        'order_product' : order_product,
    }

    return render(request, 'user/user_profile.html', context)


def order_details(request, order_id):

    order = Order.objects.get(id=order_id)
    order_items = OrderProduct.objects.filter(order_id=order)
    order_total = Decimal(order.order_total)

    # shipping_charge = 0
    # if order_total < 1000 and order_total < 902:
    #     shipping_charge = 99
    # else:
    #     shipping_charge = "Free"

    context = {
        # "shipping_charge": shipping_charge,
        "orders": order,
        "order_items": order_items,
        }

    # except Exception as e:
    #     print(e)

    return render(request, 'order/order_details.html', context)


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def add_address(request, id):

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
    # except Exception as e:
    #     print(e)

    return redirect('user_profile')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def edit_address(request, id):

    if 'email' in request.session:
        return redirect('admin_dashboard')
    
    if 'user' in request.session:

        user_address = UserAddress.objects.get(id=id)

        if request.method == 'POST':
            name = request.POST['name']
            mobile = request.POST['mobile']
            address = request.POST['address']
            city = request.POST['city']
            landmark = request.POST['landmark']
            pincode = request.POST['pincode']
            district = request.POST['district']
            state = request.POST['state']

        # Update the user_address object with new data
            user_address.name = name
            user_address.mobile = mobile
            user_address.address = address
            user_address.city = city
            user_address.landmark = landmark
            user_address.pincode = pincode
            user_address.district = district
            user_address.state = state 

            user_address.save()
            messages.success(request, "Address updated successfully!")
            return redirect('user_profile')
        

@login_required(login_url="index")
@cache_control(no_cache=True, no_store=True)
def delete_address(request, address_id):

    if "email" in request.session:
        return redirect('admin_dashboard')
    
    if "user" in request.session:

        try:
            address = UserAddress.objects.get(id=address_id)
            address.delete()
            messages.success(request, "Address deleted successfully!")

        except ObjectDoesNotExist:
            messages.error(request, "Address not found!")

    return redirect('user_profile')


@cache_control(no_cache=True, no_store=True)
def change_password(request):
    
    if "email" in request.session:
        return redirect('admin_dashboard')
        
    try:
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            if new_password == confirm_password:
                user = request.user
                user.set_password(new_password)
                user.save()
                messages.success(request, "password changed successfully!")
                return redirect("user_login")
            else:
                messages.error(request, "passwords do not match")
                return redirect("change_password")
            
        return redirect('user_profile')
        
    except Exception as e:
        print(e)
        return redirect("user_profile")