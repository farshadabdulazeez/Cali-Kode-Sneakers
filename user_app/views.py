import uuid
from django.utils import timezone
import random
import string
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
from product_app.views import calculate_percentage_discount
# Order invoice modules
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa


def index(request):

    context = {}

    categories = Category.objects.filter(is_active=True).order_by('id')
    products = Product.objects.filter(category__in=categories, is_available=True)[:8]
    firstBanner = Banner.objects.get(name="firstBanner")
    SecondBanner = Banner.objects.get(name="secondBanner")
    thirdBanner = Banner.objects.get(name="thirdBanner")

    for product in products:
        if product.category.offer:
            offer_percentage = product.category.offer
            new_selling_price = product.original_price - (product.original_price * offer_percentage / 100)
            product.selling_price = new_selling_price
        product.percentage_discount = calculate_percentage_discount(product.selling_price, product.original_price)


    context = {
        'categories' : categories,
        'products' : products,
        'firstBanner' : firstBanner,
        'SecondBanner' : SecondBanner,
        'thirdBanner' : thirdBanner
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
        if not request.POST["referral"]:
            referral = "calikode"
        else:
            referral = request.POST["referral"]

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
                user = CustomUser.objects.create_user(email, password=password, mobile=mobile, first_name=first_name, last_name=last_name)
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

                # Referral code handling
                referred_user = None
                if referral != "calikode":
                    try:
                        referred_user = CustomUser.objects.get(referral_code=referral)
                    except CustomUser.DoesNotExist:
                        referred_user = None

                if referred_user:
                    # Credit the referred user's wallet
                    referred_user.wallet += 250
                    referred_user.save()

                    # Create a transaction entry for the referred user
                    UserTransaction.objects.create(user=referred_user, transaction_type='credited', amount=250.00)

                    # Credit the referrer's wallet as well
                    user.wallet += 250
                    user.save()

                    # Create a transaction entry for the referrer
                    UserTransaction.objects.create(user=user, transaction_type='credited', amount=250.00)

                    messages.success(request, 'Referral code applied. Wallets credited for both users.')
                    
                return redirect('otp_verification', user_id)
            else:
                 messages.error(request, "Passwords do not match!")
                 return redirect('register')

    return render(request, 'user/register.html')


def generate_ref_code():
    code = str(uuid.uuid4()).replace("-", "")[:12]
    return code


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
                messages.success(request, "Logged in successfully!")
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
                
                referral_code = generate_ref_code()
                user.referral_code = referral_code
                user.save()

                referred_user = None
                if 'referral' in request.POST:
                    try:
                        referred_user = CustomUser.objects.get(referral_code=request.POST['referral'])
                    except CustomUser.DoesNotExist:
                        referred_user = None

                if referred_user:
                    # Credit the referred user's wallet
                    referred_user.wallet += 250
                    referred_user.save()

                    # Create a transaction entry for the referred user
                    UserTransaction.objects.create(user=referred_user, transaction_type='credited', amount=250.00)

                    # Credit the referrer's wallet as well
                    user.wallet += 250
                    user.save()

                    # Create a transaction entry for the referrer
                    UserTransaction.objects.create(user=user, transaction_type='credited', amount=250.00)

                    messages.success(request, 'Referral code verified. Wallets credited for both users.')

                messages.success(request, "Account successfully verified, Login now.")
                return redirect('user_login')
            else:
                messages.error(request, 'Invalid OTP, Try again')
                return redirect('otp_verificaion', user.id)
        else:
            messages.error(request, 'Please enter a valid OTP....')
    
    return render(request, 'user/otp_verification.html', context)


@cache_control(no_cache=True, no_store=True)
def forgot_password(request):
    try:
        if request.method == "POST":
            email = request.POST.get("email")
            user = CustomUser.objects.filter(email=email).first()
            if user:
                otp = get_random_string(length=6, allowed_chars="1234567890")
                user.otp = otp
                user.save()
                subject = "Verify your account"
                message = f"Your OTP for account verification in CaliKode Sneakers is {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [
                    email,
                ]
                send_mail(subject, message, email_from, recipient_list)
                return redirect("forgot_password_otp_verification", user.id)
            else:
                messages.error(request, "email id not valid")
                return redirect("forgot_password")
        return render(request, "user/forgot_password.html")
    
    except Exception as e:
        print(e)
        return render(request, "user/forgot_password.html")


@cache_control(no_cache=True, no_store=True)
def forgot_password_otp_verification(request, user_id):

    user = CustomUser.objects.get(id=user_id)
    otp = user.otp
    try:
        if request.method == "POST":
            user_otp = request.POST.get("otp")
            if user_otp == otp:
                return redirect("update_password", user.id)
            else:
                messages.error(request, "Incorrect otp")
                return redirect("forgot_password_otp_verification")
        return render(request, "user/forgot_password_otp_verification.html")
        
    except Exception as e:
        print(e)
        return render(request, "user/forgot_password_otp_verification.html")
    

@cache_control(no_cache=True, no_store=True)
def update_password(request, user_id):

    user = CustomUser.objects.get(id=user_id)
    try:
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                user.set_password(password)
                user.save()
                messages.success(request, "Password changed successfully")
                return redirect("user_login")
            else:
                messages.error(request, "passwords do not match")
                return redirect("update_password")
        return render(request, "user/update_password.html")

    except Exception as e:
        print(e)
        return render(request, "user/update_password.html")


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
    user = CustomUser.objects.get(id=user.id)
    address = UserAddress.objects.filter(user=user)
    order_product = OrderProduct.objects.filter(customer=user).order_by('-id')

    context = {
        'address' : address,
        'order_product' : order_product,
        'user' : user,
    }

    return render(request, 'user/user_profile.html', context)


@login_required(login_url="index")
def user_edit_profile(request):

    if request.method == "POST":
        # try:
        first_name = request.POST.get("edit_first_name")
        last_name = request.POST.get("edit_last_name")
        email = request.POST.get("edit_email")
        mobile = request.POST.get("edit_mobile")
        user = CustomUser.objects.get(id=request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.mobile = mobile
        user.save()
        messages.success(request, "Profile details updated!")
        return redirect("user_profile")
        # except Exception as e:
        #     print(e)
        #     messages.error(request, "An error occurred while updating your profile.")
        #     return redirect("user_profile")
    else:
        return redirect("user_profile")


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_details(request, order_id):

    order = Order.objects.get(id=order_id)
    order_items = OrderProduct.objects.filter(order_id=order)
    order_total = Decimal(order.order_total)

    context = {
        "orders": order,
        "order_items": order_items,
        }

    return render(request, 'order/order_details.html', context)


@cache_control(no_cache=True, no_store=True)
def order_cancel(request, order_id):
    if request.method == "POST":
        order_item = OrderProduct.objects.get(id=order_id)
        order = order_item.order_id
        cancel_reason = request.POST.get("cancel_reason")

        if cancel_reason:
            order.cancel_reason = cancel_reason
            order.item_cancelled = True
            order.status = "CANCELLED"
            order.save()
            order_item.save()

            total_amount = Decimal(order.order_total)
            wallet_amount = Decimal(order.wallet_amount) if order.wallet_amount else Decimal(0)
            user = order.user
            payment_method = order_item.payment.payment_method

            if payment_method == "Razorpay" or payment_method == "walletPayment" :
                # Refund total amount back to user's wallet for Razorpay payments
                refund_amount = total_amount + wallet_amount
            
            else:
                # Refund only the wallet amount for other payment methods like Cash on Delivery
                refund_amount = wallet_amount

            if user.wallet is None:
                user.wallet = Decimal(0)

            user.wallet += refund_amount
            user.save()

            # Restock products if the order is cancelled
            if order.status == "CANCELLED":
                order_products = OrderProduct.objects.filter(order_id=order)
                for order_product in order_products:
                    product_variant = order_product.variant
                    product_variant.stock += order_product.quantity
                    product_variant.save()

                user.save()
        
        return redirect('user_profile')
    # Handle GET requests or other cases not covered in the post request
    return redirect('user_profile')  # Or redirect to the appropriate page in case of a GET request


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_return(request, order_id):

    order_item = OrderProduct.objects.get(id=order_id)
    order = order_item.order_id

    if request.method == 'POST':
        return_reason = request.POST.get('return_reason')
        
        if return_reason:
            order_item.order_id.return_reason = return_reason
            order_item.order_id.item_returned = True  
            order_item.order_id.status = "RETURNED"
            order_item.order_id.save()
            order_item.save()

            wallet_amount = 0
                
            total_amount = Decimal(order.order_total)
            wallet_amount = Decimal(order.wallet_amount) 
            total_decimal = total_amount 

            user = order.user

            payment_method = order_item.payment.payment_method

            if payment_method == "Razorpay" or payment_method == "walletPayment":
                # Refund total amount back to user's wallet for Razorpay payments
                refund_amount = total_decimal + wallet_amount
                user.wallet += refund_amount
                user.save()
            else:
                # Refund only the wallet amount for Cash on Delivery
                user.wallet += wallet_amount
                user.save()

            # Restock products if the order is cancelled
            if order.status == "RETURNED":
                order_products = OrderProduct.objects.filter(order_id=order)
                for order_product in order_products:
                    product_variant = order_product.variant
                    product = product_variant.product
                    product_variant.stock += order_product.quantity
                    product_variant.save()

                user.save()

    return redirect('user_profile')


@login_required(login_url='index')
def order_invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderProduct.objects.filter(order_id=order)
    order_total = Decimal(order.order_total)
    invoice_number = f"INV-{order.order_id}"

    context = {
        "orders": order,
        "order_items": order_items,
        "invoice_number": invoice_number,
    }

    # Render the HTML template
    template = get_template('user/order_invoice.html')
    html = template.render(context)

    # Create a PDF file
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), result)

    # Return the PDF file as a response
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'

        return response

    return HttpResponse("Error generating PDF", status=500)


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
    

def blog(request):

    return render(request, 'user/blog.html')


def contact(request):

    return render(request, 'user/contact.html')