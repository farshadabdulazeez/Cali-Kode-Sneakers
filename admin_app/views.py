from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required


# @cache_control(no_cache=True, no_store=True)
def admin_login(request):
    # if 'email' in request.session:
    #     return redirect('admin_dashboard')
    
    # if request.method == 'POST':
    #     email = request.POST['email']
    #     password = request.POST['password']

    #     admin = authenticate(email=email, password=password)
        
    #     if admin:
    #         if admin.is_superuser:
    #             login(request, admin)
    #             request.session['email'] = email
    #             return redirect('admin_dashboard')
    #         else:
    #             messages.error(request, "You can't access this session with user credentials.")
    #     else:
    #         messages.error(request, "Invalid credentials, try again with valid credentials.")
    return render(request, 'admin/admin_login.html')



# @staff_member_required(login_url='admin_login')
# def admin_dashboard(request):
    # if 'email' not in request.session:
    #     return redirect('admin_login')

    # return render(request, 'admin/index.html')

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_logout(request):
    # logout(request)
    # request.session.flush()
    # return redirect('admin_login')