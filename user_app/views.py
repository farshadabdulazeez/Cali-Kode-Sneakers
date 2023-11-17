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
from django.http import HttpResponse, HttpResponseServerError
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
    try:
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
            'categories': categories,
            'products': products,
            'firstBanner': firstBanner,
            'SecondBanner': SecondBanner,
            'thirdBanner': thirdBanner
        }

        return render(request, 'user/index.html', context)

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        return HttpResponseServerError(f"An error occurred: {str(e)}")


@cache_control(no_cache=True, no_store=True)
def register(request):
    try:
        # Check if the user is already logged in
        if 'email' in request.session:
            return redirect('admin_dashboard')
        if 'user' in request.session:
            return redirect('index')

        # Handle the registration form submission
        if request.method == 'POST':
            # Retrieve form data
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            user_name = request.POST.get('username')
            email = request.POST.get('email')
            mobile = request.POST.get('mobile')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            # Referral code handling
            referral = request.POST.get('referral', 'calikode')  # default referral code is 'calikode'
            referred_user = None

            # Check and handle referral code
            if referral != "calikode":
                try:
                    referred_user = CustomUser.objects.get(referral_code=referral)
                except CustomUser.DoesNotExist:
                    messages.error(request, "Invalid referral code!")
                    return redirect('register')

            # Check for existing email and mobile
            existing_email = CustomUser.objects.filter(email=email)
            existing_mobile = CustomUser.objects.filter(mobile=mobile)

            if existing_email:
                messages.error(request, "Email is already existing!")
                return redirect('register')
            elif existing_mobile:
                messages.error(request, "Mobile is already existing!")
                return redirect('register')
            else:
                # Create user and send OTP for verification
                if password == confirm_password:
                    user = CustomUser.objects.create_user(email, password=password, mobile=mobile, first_name=first_name, last_name=last_name)
                    user_id = user.id
                    otp = get_random_string(length=6, allowed_chars='1234567890')

                    # Send OTP via email
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
                
                    # Save OTP and handle referral rewards
                    user.otp = otp
                    user.save()

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
                    
                    # Redirect to OTP verification page
                    return redirect('otp_verification', user_id)
                else:
                    messages.error(request, "Passwords do not match!")
                    return redirect('register')

        # Render the registration form page
        return render(request, 'user/register.html')

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        return HttpResponseServerError(f"An error occurred: {str(e)}")


def generate_ref_code():
    code = str(uuid.uuid4()).replace("-", "")[:12]
    return code


@cache_control(no_cache=True, no_store=True)
def user_login(request):
    try:
        # Check if the user is already logged in
        if 'email' in request.session:
            return redirect('admin_dashboard')
        if 'user' in request.session:
            return redirect('index')

        # Handle the login form submission
        if request.method == 'POST':
            email = request.POST['email']
            password = request.POST['password']

            # Authenticate user
            user = authenticate(request, username=email, password=password)

            if user:
                # Log in user and set session
                request.session['user'] = email
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('index')
            else:
                # Invalid credentials, redirect to login page with error message
                messages.error(request, "Invalid Credentials, Try again!")
                return redirect('user_login')

        # Render the login form page
        return render(request, 'user/user_login.html')

    except Exception as e:

        return HttpResponseServerError(f"An error occurred: {str(e)}")


@cache_control(no_cache=True, no_store=True)
def otp_verification(request, user_id):
    try:
        # Check if the user is already logged in
        if 'email' in request.session:
            return redirect('admin_dashboard')
        if 'user' in request.session:
            return redirect('index')

        # Retrieve the user based on the user_id
        user = CustomUser.objects.get(id=user_id)

        context = {
            'user': user,
        }

        if request.method == 'POST':
            otp = request.POST['otp']

            if len(otp) == 6:
                if otp == user.otp:
                    # Update user verification status and clear OTP
                    user.is_verified = True
                    user.otp = ''
                    user.save()

                    # Generate and set referral code
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
                    return redirect('otp_verification', user.id)
            else:
                messages.error(request, 'Please enter a valid OTP....')

        return render(request, 'user/otp_verification.html', context)

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        return HttpResponseServerError(f"An error occurred: {str(e)}")
    


@cache_control(no_cache=True, no_store=True)
def forgot_password(request):
    try:
        # Check if the user is already logged in
        if 'email' in request.session:
            return redirect('admin_dashboard')
        if 'user' in request.session:
            return redirect('index')

        if request.method == "POST":
            email = request.POST.get("email")
            user = CustomUser.objects.filter(email=email).first()

            if user:
                # Generate OTP and save it to the user's model
                otp = get_random_string(length=6, allowed_chars="1234567890")
                user.otp = otp
                user.save()

                # Send OTP via email
                subject = "Verify your account"
                message = f"Your OTP for account verification in CaliKode Sneakers is {otp}"
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [email, ]
                send_mail(subject, message, email_from, recipient_list)

                # Redirect to OTP verification page
                return redirect("forgot_password_otp_verification", user.id)
            else:
                # Invalid email, show error message
                messages.error(request, "Email ID not valid")
                return redirect("forgot_password")

        # Render the forgot password page
        return render(request, "user/forgot_password.html")

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        print(e)
        return render(request, "user/forgot_password.html")


@cache_control(no_cache=True, no_store=True)
def forgot_password_otp_verification(request, user_id):
    try:
        # Retrieve the user based on the user_id
        user = CustomUser.objects.get(id=user_id)
        otp = user.otp

        if request.method == "POST":
            user_otp = request.POST.get("otp")

            if user_otp == otp:
                # Redirect to update password page if OTP is correct
                return redirect("update_password", user.id)
            else:
                # Incorrect OTP, show error message
                messages.error(request, "Incorrect OTP")
                return redirect("forgot_password_otp_verification")

        # Render the OTP verification page
        return render(request, "user/forgot_password_otp_verification.html")

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        print(e)
        return render(request, "user/forgot_password_otp_verification.html")
  

@cache_control(no_cache=True, no_store=True)
def update_password(request, user_id):
    try:
        # Retrieve the user based on the user_id
        user = CustomUser.objects.get(id=user_id)

        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password == confirm_password:
                # Set the new password and save the user
                user.set_password(password)
                user.save()

                # Display success message and redirect to login
                messages.success(request, "Password changed successfully")
                return redirect("user_login")
            else:
                # Passwords do not match, show error message
                messages.error(request, "Passwords do not match")
                return redirect("update_password")

        # Render the update password page
        return render(request, "user/update_password.html")

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        print(e)
        return render(request, "user/update_password.html")
 

@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def user_logout(request):
    try:
        # Check if the user is already logged in
        if 'email' in request.session:
            return redirect('admin_dashboard')
        
        # Check if the user is logged in and perform logout
        if 'user' in request.session:
            logout(request)
            request.session.flush()
            messages.success(request, 'Logout successfully!')

        # Redirect to the index page
        return redirect('index')

    except Exception as e:
        # Log the exception or handle it appropriately
        # In development, you can also return a detailed error response
        print(e)
        return redirect('index') 
    

@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def user_profile(request):
    try:
        # Check if the user is an admin
        if 'email' in request.session:
            return redirect('admin_dashboard') 

        if 'user' in request.session:
            user = request.user

            # Retrieve the user object from the database
            user = CustomUser.objects.get(id=user.id)

            # Retrieve user's addresses and order products
            address = UserAddress.objects.filter(user=user)
            order_product = OrderProduct.objects.filter(customer=user).order_by('-id')

            # Prepare context for rendering the template
            context = {
                'address' : address,
                'order_product' : order_product,
                'user' : user,
            }

            # Render the user profile template with the context
            return render(request, 'user/user_profile.html', context)

    except CustomUser.DoesNotExist:
        # Handle the case where the user does not exist
        messages.error(request, "User does not exist.")
        return redirect('index')

    except Exception as e:
        # Log the exception or handle it appropriately
        messages.error(request, "An error occurred.")
        return redirect('index')


@login_required(login_url="index")
def user_edit_profile(request):
    if request.method == "POST":
        try:
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
        except Exception as e:
            # Log the exception or handle it as needed
            print(e)
            messages.error(request, "An error occurred while updating your profile.")
            return redirect("user_profile")
    else:
        return redirect("user_profile")
    

@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_details(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        order_items = OrderProduct.objects.filter(order_id=order)
        order_total = Decimal(order.order_total)

        context = {
            "orders": order,
            "order_items": order_items,
        }

        return render(request, 'order/order_details.html', context)
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist.")
        return redirect("index")  # Adjust the redirect URL as needed
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "An error occurred while retrieving order details.")
        return redirect("index")  # Adjust the redirect URL as needed


@cache_control(no_cache=True, no_store=True)
def order_cancel(request, order_id):
    try:
        if request.method == "POST":
            order_item = get_object_or_404(OrderProduct, id=order_id)
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

                if payment_method == "Razorpay" or payment_method == "walletPayment":
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

                messages.success(request, "Order has been cancelled successfully!")

            return redirect('user_profile')
        # Handle GET requests or other cases not covered in the post request
        return redirect('user_profile')  # Or redirect to the appropriate page in case of a GET request
    except OrderProduct.DoesNotExist:
        messages.error(request, "Order product does not exist.")
        return redirect("user_profile")  # Adjust the redirect URL as needed
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "An error occurred while cancelling the order.")
        return redirect("user_profile")  # Adjust the redirect URL as needed
    

@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def order_return(request, order_id):
    try:
        # Retrieve the order product based on the provided order ID
        order_item = get_object_or_404(OrderProduct, id=order_id)
        order = order_item.order_id

        if request.method == 'POST':
            # Retrieve the return reason from the form
            return_reason = request.POST.get('return_reason')

            if return_reason:
                # Update order information for the return
                order_item.order_id.return_reason = return_reason
                order_item.order_id.item_returned = True
                order_item.order_id.status = "RETURNED"
                order_item.order_id.save()
                order_item.save()

                # Initialize wallet amount
                wallet_amount = 0

                # Retrieve total and wallet amounts from the order
                total_amount = Decimal(order.order_total)
                wallet_amount = Decimal(order.wallet_amount)
                total_decimal = total_amount

                # Retrieve the user associated with the order
                user = order.user

                # Determine the payment method used for the order item
                payment_method = order_item.payment.payment_method

                if payment_method in ["Razorpay", "walletPayment", "cash_on_delivery"]:
                # Refund total amount back to user's wallet for all specified payment methods
                    refund_amount = total_decimal + wallet_amount
                    user.wallet += refund_amount
                    user.save()
                else:
                    # Refund only the wallet amount for Cash on Delivery
                    user.wallet += wallet_amount
                    user.save()

                # Restock products if the order is returned
                if order.status == "RETURNED":
                    order_products = OrderProduct.objects.filter(order_id=order)
                    for order_product in order_products:
                        product_variant = order_product.variant
                        product = product_variant.product
                        product_variant.stock += order_product.quantity
                        product_variant.save()

                    user.save()

                messages.success(request, "Order has been returned successfully!")

        return redirect('user_profile')
    except OrderProduct.DoesNotExist:
        # Handle the case where the order product does not exist
        messages.error(request, "Order product does not exist.")
        return redirect("user_profile")  # Adjust the redirect URL as needed
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "An error occurred while processing the return.")
        return redirect("user_profile")  # Adjust the redirect URL as needed
 

@login_required(login_url='index')
def order_invoice(request, order_id):
    """
    View to generate and download an invoice in PDF format for a specific order.

    Args:
        request (HttpRequest): The HTTP request object.
        order_id (int): The ID of the order for which the invoice is generated.

    Returns:
        HttpResponse: The HTTP response with the generated PDF invoice.
    """
    try:
        # Retrieve the order and related order items
        order = get_object_or_404(Order, id=order_id)
        order_items = OrderProduct.objects.filter(order_id=order)

        # Calculate the order total and create an invoice number
        order_total = Decimal(order.order_total)
        invoice_number = f"INV-{order.order_id}"

        # Prepare context data for rendering the HTML template
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
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        messages.error(request, "Order does not exist.")
        return redirect("user_profile")  # Adjust the redirect URL as needed
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        messages.error(request, "An error occurred while generating the invoice.")
        return redirect("user_profile")  # Adjust the redirect URL as needed


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def add_address(request, id):
    try:
        # Redirect if an admin is trying to access the user functionality
        if 'email' in request.session:
            return redirect('admin_dashboard')
        
        # Get the user from the session
        if 'user' in request.session:
            user = request.user
            
        # Process the form submission
        if request.method == 'POST':
            # Get form data
            name = request.POST['name']
            mobile = request.POST['mobile']
            address = request.POST['address']
            city = request.POST['city']
            landmark = request.POST['landmark']
            pincode = request.POST['pincode']
            district = request.POST['district']
            state = request.POST['state']

            # Use the user's first name if name is not provided
            if not name:
                name = user.first_name

            # Validate mobile number length
            if len(mobile) == 10:
                # Create and save the UserAddress instance
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

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('user_profile')


@login_required(login_url='index')
@cache_control(no_cache=True, no_store=True)
def edit_address(request, id):
    try:
        # Redirect if an admin is trying to access the user functionality
        if 'email' in request.session:
            return redirect('admin_dashboard')
        
        # Get the user_address instance to be edited
        if 'user' in request.session:
            user_address = UserAddress.objects.get(id=id)

            # Process the form submission
            if request.method == 'POST':
                # Get form data
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

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('user_profile')


@login_required(login_url="index")
@cache_control(no_cache=True, no_store=True)
def delete_address(request, address_id):
    try:
        # Redirect if an admin is trying to access the user functionality
        if "email" in request.session:
            return redirect('admin_dashboard')
        
        # Delete the address if it exists, otherwise, handle the exception
        if "user" in request.session:
            try:
                address = UserAddress.objects.get(id=address_id)
                address.delete()
                messages.success(request, "Address deleted successfully!")

            except ObjectDoesNotExist:
                messages.error(request, "Address not found!")

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect('user_profile')
        

@login_required(login_url="index")
@cache_control(no_cache=True, no_store=True)
def change_password(request):
    try:
        # Redirect if an admin is trying to access the user functionality
        if "email" in request.session:
            return redirect('admin_dashboard')
            
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            
            # Check if new password and confirm password match
            if new_password == confirm_password:
                user = request.user
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully!")
                return redirect("user_login")
            else:
                messages.error(request, "Passwords do not match")
                return redirect("change_password")
                
        return redirect('user_profile')
        
    except Exception as e:
        # Log the exception or handle it as needed
        print(e)
        return redirect("user_profile")
    

def blog(request):

    return render(request, 'user/blog.html')


def contact(request):

    return render(request, 'user/contact.html')