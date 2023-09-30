from .models import *
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout


def index(request):

    return render(request, 'user/index.html')



@cache_control(no_cache=True, no_store=True)
def register(request):

    # if 'email' in request.session:
    #     return redirect('admin_dashboard')
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

    # if 'email' in request.session:
    #     return redirect('admin_dashboard')
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
    # if 'email' in request.session:
    #     return redirect('admin_dashboard')
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

    # if 'email' in request.session:
    #     return redirect('admin_dashboard')
    if 'user' in request.session:
        logout(request)
        request.session.flush()
        messages.success(request, 'Logout successfully!')
    return redirect('index')