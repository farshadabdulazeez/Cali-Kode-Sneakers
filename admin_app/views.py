import json
import os
from django.forms import ValidationError
from order.models import *
from decimal import Decimal
from user_app.models import *
from product_app.models import *
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import cache_control
from django.contrib.auth import authenticate, login, logout
from django.db.models.functions import TruncDate
from django.contrib.admin.views.decorators import staff_member_required
from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa 
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractDay
from django.db.models import Sum, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from django.utils.dateparse import parse_date
from django.utils.timezone import make_aware
from datetime import timedelta


# @cache_control(no_cache=True, no_store=True)
# def admin_login(request):  
    
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']

#         admin = authenticate(email=email, password=password)
        
#         if admin:
#             if admin.is_superuser:
#                 login(request, admin)
#                 request.session['email'] = email
#                 return redirect('admin_users')
#             else:
#                 messages.error(request, "You can't access this session with user credentials.")
#         else:
#             messages.error(request, "Invalid credentials, try again with valid credentials.")
#     return render(request, 'admin/admin_login.html')


# Decorator to specify cache control directives for this view
@cache_control(no_cache=True, no_store=True)
def admin_login(request):  
    try:
        # Check if the request method is POST
        if request.method == 'POST':
            # Get the email and password from the POST data
            email = request.POST['email']
            password = request.POST['password']

            # Authenticate the user
            admin = authenticate(email=email, password=password)

            # Check if authentication is successful
            if admin:
                # Check if the authenticated user is a superuser
                if admin.is_superuser:
                    # Log in the user and store the email in the session
                    login(request, admin)
                    request.session['email'] = email
                    messages.success(request, 'Logged in successfully')
                    # Redirect to the 'admin_users' view
                    return redirect('admin_dashboard')
                else:
                    # Display an error message if the user is not a superuser
                    messages.error(request, "You can't access this session with user credentials.")
            else:
                # Display an error message for invalid credentials
                messages.error(request, "Invalid credentials, try again with valid credentials.")
    except Exception as e:
        # If an exception occurs, render a custom error template with the exception message
        return render(request, 'error_404.html')

    # Render the 'admin_login' template
    return render(request, 'admin/admin_login.html')


# @staff_member_required(login_url='admin_login')
# def admin_dashboard(request):

#     if 'email' not in request.session:  # Check for the absence of 'email' in session
#         return redirect('admin_login')

#     order = 0 * [12]
#     order_count = 0 * [12]
#     cancelled_orders_count = 0
#     returned_orders_count = 0
#     successfull_orders_count = 0
#     cash_on_delivery_count = 0
#     razorpay_count = 0

#     orders = Order.objects.all().order_by('id')
#     order_count = orders.count()
#     order_total = Order.objects.aggregate(total = Sum('order_total'))['total']
#     cancelled_orders = Order.objects.filter(status="CANCELLED")
#     returned_orders = Order.objects.filter(status="RETURNED")
#     successfull_orders = Order.objects.filter(status="DELIVERED")
#     cancelled_orders_count = Order.objects.filter(status="CANCELLED").count()
#     returned_orders_count = Order.objects.filter(status="RETURNED").count()
#     successfull_orders_count = Order.objects.filter(status="DELIVERED").count()
#     cash_on_delivery_count = Payments.objects.filter(payment_method ='cash_on_delivery').count()
#     razorpay_count = Payments.objects.filter(payment_method ='Razorpay').count()
#     total_revenue = Order.objects.aggregate(total_revenue = Sum('order_total'))['total_revenue']
#     total_revenue = float(total_revenue)
#     total_profit = total_revenue * 0.20
#     # Inside your admin_dashboard view
#     product_sales = OrderProduct.objects.values('variant__product').annotate(sales=Sum('quantity')).order_by('-sales')

#     # Get the top-selling products based on the number of sales
#     top_selling_products = product_sales.filter(sales__gt=0).order_by('-sales')[:5]


#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')

#     # Retain the full dataset for pagination
#     orders = Order.objects.all().order_by('id')

#     if start_date and end_date:
#         try:
#             start_datetime = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
#             # Increment the end date by one day to make it inclusive
#             end_datetime = make_aware(datetime.strptime(end_date, '%Y-%m-%d')) + timedelta(days=1)
            
#             filtered_orders = orders.filter(created__range=(start_datetime, end_datetime))
#         except ValueError:
#             return HttpResponse("Invalid date format. Please use YYYY-MM-DD format.")
#     else:
#         filtered_orders = orders

#     # Search functionality
#     query = request.GET.get('q')
#     if query:
#         filtered_orders = filtered_orders.filter(
#             Q(order_id__icontains=query) | Q(address__name__icontains=query)
#         )

#     # Pagination
#     page = request.GET.get('page', 1)
#     paginator = Paginator(filtered_orders, 10)
#     try:
#         orders = paginator.page(page)
#     except PageNotAnInteger:
#         orders = paginator.page(1)
#     except EmptyPage:
#         orders = paginator.page(paginator.num_pages)

#     # Retrieve the daily sales data
#     daily_sales = (
#         Order.objects.annotate(day=ExtractDay('created'))
#         .values('day')
#         .annotate(total_sales=Sum('order_total'))
#         .order_by('day')
#     )

#     # Prepare an empty dictionary for daily sales
#     daily_sales_data = {day: 0 for day in range(1, 32)}  # Assuming days range from 1 to 31

#     # Update the dictionary with sales data where available
#     for day_data in daily_sales:
#         day = day_data['day']
#         daily_sales_data[day] = day_data['total_sales']

#     daily_sales_json = json.dumps({
#         'xValues': list(range(1, 32)),  # Days range
#         'yValues': list(daily_sales_data.values()),  # Sales data for each day
#         'barColors': ["red", "green", "blue", "orange", "brown"]  # Colors
#     })

#     # Retrieve the yearly sales data
#     yearly_sales = (
#         Order.objects.annotate(year=ExtractYear('created'))
#         .values('year')
#         .annotate(total_sales=Sum('order_total'))
#         .order_by('year')
#     )

#     # Prepare an empty dictionary for yearly sales
#     yearly_sales_data = {year: 0 for year in range(2022, 2030)}  # Adjust the year range as needed

#     # Update the dictionary with sales data where available
#     for year_data in yearly_sales:
#         year = year_data['year']
#         yearly_sales_data[year] = year_data['total_sales']

#     yearly_sales_json = json.dumps({
#         'xValues': list(range(2022, 2030)),  # Year range
#         'yValues': list(yearly_sales_data.values()),  # Sales data for each year
#         'barColors': ["red", "green", "blue", "orange", "brown"]  # Colors
#     })

#     # Generate a dictionary with all months
#     months = {
#         1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
#         5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
#         9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
#     }

#     # Retrieve the monthly sales data
#     monthly_sales = (
#         Order.objects.annotate(month=ExtractMonth('created'))
#         .values('month')
#         .annotate(total_sales=Sum('order_total'))
#         .order_by('month')
#     )

#     # Prepare an empty dictionary for monthly sales
#     monthly_sales_data = {month: 0 for month in months.values()}

#     # Update the dictionary with sales data where available
#     for month_data in monthly_sales:
#         month_name = months[month_data['month']]
#         monthly_sales_data[month_name] = month_data['total_sales']

#     # Convert the data to JSON for Chart.js
#     monthly_sales_json = json.dumps({
#     'xValues': list(months.values()),  # Month names
#     'yValues': list(monthly_sales_data.values()),  # Sales data for each month
#     'barColors': ["red", "green", "blue", "orange", "brown"]  # Colors
# })


#     context = {
#         'orders' : orders,
#         'order_count' : order_count,
#         'order_total' : order_total,
#         'cancelled_orders' : cancelled_orders,
#         'returned_orders' : returned_orders,
#         'successfull_orders' : successfull_orders,
#         'cancelled_orders_count' : cancelled_orders_count,
#         'returned_orders_count' : returned_orders_count,
#         'successfull_orders_count' : successfull_orders_count,
#         'cash_on_delivery_count' : cash_on_delivery_count,
#         'razorpay_count' : razorpay_count,
#         'total_revenue' : total_revenue,
#         'total_profit' : total_profit,
#         'monthly_sales_data': monthly_sales_json,
#         'daily_sales_data': daily_sales_json,
#         'yearly_sales_data': yearly_sales_json,
#         'start_date': start_date,
#         'end_date': end_date,
#         'top_selling_products': top_selling_products,
#     }

#     return render(request, 'admin/admin_dashboard.html', context)


@staff_member_required(login_url='admin_login')
def admin_dashboard(request):
    try:
        if 'email' not in request.session:
            return redirect('admin_login')

        order = 0 * [12]
        order_count = 0 * [12]
        cancelled_orders_count = 0
        returned_orders_count = 0
        successfull_orders_count = 0
        cash_on_delivery_count = 0
        razorpay_count = 0

        orders = Order.objects.all().order_by('id')
        order_count = orders.count()
        order_total = Order.objects.aggregate(total=Sum('order_total'))['total']
        cancelled_orders = Order.objects.filter(status="CANCELLED")
        returned_orders = Order.objects.filter(status="RETURNED")
        successfull_orders = Order.objects.filter(status="DELIVERED")
        cancelled_orders_count = Order.objects.filter(status="CANCELLED").count()
        returned_orders_count = Order.objects.filter(status="RETURNED").count()
        successfull_orders_count = Order.objects.filter(status="DELIVERED").count()
        cash_on_delivery_count = Payments.objects.filter(payment_method='cash_on_delivery').count()
        razorpay_count = Payments.objects.filter(payment_method='Razorpay').count()
        total_revenue = Order.objects.aggregate(total_revenue=Sum('order_total'))['total_revenue']
        total_revenue = float(total_revenue)
        total_profit = total_revenue * 0.20

        # Inside your admin_dashboard view
        product_sales = OrderProduct.objects.values('variant__product').annotate(sales=Sum('quantity')).order_by('-sales')

        # Get the top-selling products based on the number of sales
        top_selling_products = product_sales.filter(sales__gt=0).order_by('-sales')[:5]

        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        # Retain the full dataset for pagination
        orders = Order.objects.all().order_by('id')

        if start_date and end_date:
            try:
                start_datetime = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
                # Increment the end date by one day to make it inclusive
                end_datetime = make_aware(datetime.strptime(end_date, '%Y-%m-%d')) + timedelta(days=1)

                filtered_orders = orders.filter(created__range=(start_datetime, end_datetime))
            except ValueError:
                return HttpResponse("Invalid date format. Please use YYYY-MM-DD format.")
        else:
            filtered_orders = orders

        # Search functionality
        query = request.GET.get('q')
        if query:
            filtered_orders = filtered_orders.filter(
                Q(order_id__icontains=query) | Q(address__name__icontains=query)
            )

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(filtered_orders, 10)
        try:
            orders = paginator.page(page)
        except PageNotAnInteger:
            orders = paginator.page(1)
        except EmptyPage:
            orders = paginator.page(paginator.num_pages)

        # Retrieve the daily sales data
        daily_sales = (
            Order.objects.annotate(day=ExtractDay('created'))
            .values('day')
            .annotate(total_sales=Sum('order_total'))
            .order_by('day')
        )

        # Prepare an empty dictionary for daily sales
        daily_sales_data = {day: 0 for day in range(1, 32)}  # Assuming days range from 1 to 31

        # Update the dictionary with sales data where available
        for day_data in daily_sales:
            day = day_data['day']
            daily_sales_data[day] = day_data['total_sales']

        daily_sales_json = json.dumps({
            'xValues': list(range(1, 32)),  # Days range
            'yValues': list(daily_sales_data.values()),  # Sales data for each day
            'barColors': ["red", "green", "blue", "orange", "brown"]  # Colors
        })

        # Retrieve the yearly sales data
        yearly_sales = (
            Order.objects.annotate(year=ExtractYear('created'))
            .values('year')
            .annotate(total_sales=Sum('order_total'))
            .order_by('year')
        )

        # Prepare an empty dictionary for yearly sales
        yearly_sales_data = {year: 0 for year in range(2022, 2030)}  # Adjust the year range as needed

        # Update the dictionary with sales data where available
        for year_data in yearly_sales:
            year = year_data['year']
            yearly_sales_data[year] = year_data['total_sales']

        yearly_sales_json = json.dumps({
            'xValues': list(range(2022, 2030)),  # Year range
            'yValues': list(yearly_sales_data.values()),  # Sales data for each year
            'barColors': ["red", "green", "blue", "orange", "brown"]  # Colors
        })

        # Generate a dictionary with all months
        months = {
            1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
            5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
            9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
        }

        # Retrieve the monthly sales data
        monthly_sales = (
            Order.objects.annotate(month=ExtractMonth('created'))
            .values('month')
            .annotate(total_sales=Sum('order_total'))
            .order_by('month')
        )

        # Prepare an empty dictionary for monthly sales
        monthly_sales_data = {month: 0 for month in months.values()}

        # Update the dictionary with sales data where available
        for month_data in monthly_sales:
            month_name = months[month_data['month']]
            monthly_sales_data[month_name] = month_data['total_sales']

        # Convert the data to JSON for Chart.js
        monthly_sales_json = json.dumps({
            'xValues': list(months.values()),  # Month names
            'yValues': list(monthly_sales_data.values()),  # Sales data for each month
            'barColors': ["red", "green", "blue", "orange", "brown"]  # Colors
        })

        context = {
            'orders': orders,
            'order_count': order_count,
            'order_total': order_total,
            'cancelled_orders': cancelled_orders,
            'returned_orders': returned_orders,
            'successfull_orders': successfull_orders,
            'cancelled_orders_count': cancelled_orders_count,
            'returned_orders_count': returned_orders_count,
            'successfull_orders_count': successfull_orders_count,
            'cash_on_delivery_count': cash_on_delivery_count,
            'razorpay_count': razorpay_count,
            'total_revenue': total_revenue,
            'total_profit': total_profit,
            'monthly_sales_data': monthly_sales_json,
            'daily_sales_data': daily_sales_json,
            'yearly_sales_data': yearly_sales_json,
            'start_date': start_date,
            'end_date': end_date,
            'top_selling_products': top_selling_products,
        }

        return render(request, 'admin/admin_dashboard.html', context)

    except Exception as e:
        # Log the exception or handle it accordingly
        print(f"An error occurred: {str(e)}")
        return render(request, 'error_404.html')


@staff_member_required(login_url='admin_login') 
def admin_order_details(request, order_id):
    try:
        if 'email' not in request.session:
            return redirect('admin_login')

        order = Order.objects.get(order_id=order_id)
        order_items = OrderProduct.objects.filter(order_id=order)
        order_total = Decimal(order.order_total)
        invoice_number = f"INV-{order.order_id}"

        context = {
            "orders": order,
            "order_items": order_items,
            "invoice_number": invoice_number,
        }

        return render(request, 'admin/admin_order_details.html', context)

    except Order.DoesNotExist:
        # Handle the case where the order with the given ID does not exist
        messages.error(request, "Order not found")
        return redirect('admin_dashboard')
    except Exception as e:
        # Log the exception or handle it accordingly
        print(f"An error occurred: {str(e)}")
        return render(request, 'error_404.html')


@staff_member_required(login_url='admin_login') 
def admin_sales_report(request):
    try:
        if 'email' not in request.session:
            return redirect('admin_login')

        orders = Order.objects.all().order_by('id')

        context = {
            'orders': orders
        }

        if 'pdf' in request.GET:  # Check if the request asks for PDF download
            template_path = 'admin/admin_sales_report.html'  # Your HTML template path

            # Render template
            template = get_template(template_path)
            html = template.render(context)

            # Create a PDF
            response = BytesIO()
            pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)

            if not pdf.err:
                # Return PDF as a downloadable file
                response.seek(0)
                return HttpResponse(response, content_type='application/pdf')

        return render(request, 'admin/admin_sales_report.html', context)

    except Exception as e:
        # Log the exception or handle it accordingly
        print(f"An error occurred: {str(e)}")
        return render(request, 'error_404.html')



# @staff_member_required(login_url='admin_login') 
# def admin_order_details(request, order_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     order = Order.objects.get(order_id=order_id)
#     order_items = OrderProduct.objects.filter(order_id=order)
#     order_total = Decimal(order.order_total)
#     invoice_number = f"INV-{order.order_id}"

#     context = {
#         "orders": order,
#         "order_items": order_items,
#         "invoice_number" : invoice_number,
#     }

#     return render(request, 'admin/admin_order_details.html', context)


# @staff_member_required(login_url='admin_login') 
# def admin_sales_report(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     orders = Order.objects.all().order_by('id')

#     context = {
#         'orders' : orders
#     }

#     if 'pdf' in request.GET:  # Check if the request asks for PDF download
#         template_path = 'admin/admin_sales_report.html'  # Your HTML template path

#         # Render template
#         template = get_template(template_path)
#         html = template.render(context)

#         # Create a PDF
#         response = BytesIO()
#         pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)

#         if not pdf.err:
#             # Return PDF as a downloadable file
#             response.seek(0)
#             return HttpResponse(response, content_type='application/pdf')

#     return render(request, 'admin/admin_sales_report.html', context)


# @staff_member_required(login_url='admin_login')
# def admin_users(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     context = {}
#     try:
#         users = CustomUser.objects.all().order_by('id')
#         context = {
#             'users' : users,
#         }
#     except Exception as e:
#         print(e)

#     return render(request, 'admin/admin_users.html', context)



# Decorator to ensure only staff members can access the view
@staff_member_required(login_url='admin_login')
def admin_users(request):
    # Check if 'email' is not present in the session, redirect to admin_login
    if 'email' not in request.session:
        return redirect('admin_login')

    # Initialize an empty context dictionary
    context = {}

    try:
        # Retrieve all users and order them by 'id'
        users = CustomUser.objects.all().order_by('id')

        # Create a context dictionary with the retrieved users
        context = {
            'users': users,
        }
    except Exception as e:
        # If an exception occurs, print it for debugging purposes
        print(e)

        # Render a custom error template with the exception message
        return render(request, 'error_404.html')

    # Render the template with the determined context
    return render(request, 'admin/admin_users.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_users_control(request, id):
    # Check if 'email' is not present in the session, redirect to admin_login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Retrieve the user based on the provided id
        user = CustomUser.objects.get(id=id)

        # Toggle the user's 'is_active' status
        if user.is_active:
            # Log out the user if they are currently logged in
            if user == request.user:
                logout(request)
                request.session.flush()
            user.is_active = False
        else:
            user.is_active = True

        # Save the changes to the user
        user.save()
    except Exception as e:
        # If an exception occurs, print it for debugging purposes
        print(e)

    # Redirect to the 'admin_users' view after processing
    return redirect('admin_users')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_users_control(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         user = CustomUser.objects.get(id=id)
#         if user.is_active:
#             # Log out the user if they are currently logged in
#             if user == request.user:
#                 logout(request)
#                 request.session.flush()
#             user.is_active = False
#         else:
#             user.is_active = True
#         user.save()
#     except Exception as e:
#         print(e)

#     return redirect('admin_users')


# @staff_member_required(login_url='admin_login')
# def admin_category(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     context = {}
#     try:
#         categories = Category.objects.all().order_by('id')
#         context = {
#             'categories': categories
#         }
#     except Exception as e:
#         print(e)

#     return render(request, 'admin/admin_category.html', context)


@staff_member_required(login_url='admin_login')
def admin_category(request):
    # Check if 'email' is not present in the session, redirect to admin_login
    if 'email' not in request.session:
        return redirect('admin_login')

    # Initialize an empty context dictionary
    context = {}

    try:
        # Retrieve all categories and order them by 'id'
        categories = Category.objects.all().order_by('id')

        # Create a context dictionary with the retrieved categories
        context = {
            'categories': categories
        }
    except Exception as e:
        # If an exception occurs, print it for debugging purposes
        print(e)

    # Render the template with the determined context
    return render(request, 'admin/admin_category.html', context)


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_add_category(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         if request.method == 'POST':
#             category_name = request.POST['category_name']
#             category_slug = category_name.replace("-"," ")
#             existing_category = Category.objects.filter(category_name__iexact=category_name)
           
#             if existing_category.exists():
#                 messages.error(request, 'Category exists!')
#                 return redirect('admin_add_category')
            
#             category = Category(
#                 category_name = category_name,
#                 category_description = request.POST['category_description'],
#                 slug= category_slug,
#                 offer=request.POST.get('category_offer')
#             )

#             if request.FILES:
#                 category.category_image = request.FILES['category_image']

#             category.save()
#             messages.success(request, 'Category added!')
#             return redirect('admin_category')
        
#     except Exception as e:
#         print(e)

#     return render(request, 'admin/admin_add_category.html')


@staff_member_required(login_url='admin_login')
def admin_add_category(request):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Handle form submission (POST request)
        if request.method == 'POST':
            # Extract data from the POST request
            category_name = request.POST['category_name']
            category_slug = category_name.replace("-", " ")

            # Check if a category with the same name already exists
            existing_category = Category.objects.filter(category_name__iexact=category_name)
            if existing_category.exists():
                # Display an error message and redirect to the same page
                messages.error(request, 'Category already exists!')
                return redirect('admin_add_category')

            # Create a new category instance and set its attributes
            category = Category(
                category_name=category_name,
                category_description=request.POST['category_description'],
                slug=category_slug,
                offer=request.POST.get('category_offer')
            )

            # Check if there is a file in the request and save it
            if request.FILES:
                category.category_image = request.FILES['category_image']

            # Save the category to the database
            category.save()

            # Display a success message and redirect to the admin category page
            messages.success(request, 'Category added successfully!')
            return redirect('admin_category')

    except Exception as e:
        # Catch any exceptions that might occur
        return render(request,'error_404.html')

    # Render the template
    return render(request, 'admin/admin_add_category.html')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_edit_category(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         category = Category.objects.get(id=id)

#         context = {
#             'category': category,
#         }

#         if request.method == 'POST':
#             if 'category_image' in request.FILES:
#                 if category.category_image:
#                     os.remove(category.category_image.path)
#                 category.category_image = request.FILES['category_image']
#             category.category_name = request.POST['category_name']
#             category.category_description = request.POST['category_description']
#             # Check if offer field exists in the form submission
#             if 'category_offer' in request.POST:
#                 category_offer = int(request.POST['category_offer'])
#                 category.offer = category_offer
                
#             category.save()

#             messages.success(request, "Category Updated!")
#             return redirect('admin_category')
        
#         return render(request, 'admin/admin_edit_category.html', context)
    
#     except Exception as e:
#         print(e)

#         return redirect('admin_category')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_category(request, id):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Retrieve the category with the specified id
        category = Category.objects.get(id=id)

        # Prepare the context with the category data
        context = {
            'category': category,
        }

        # Handle form submission (POST request)
        if request.method == 'POST':
            # Check if 'category_image' is in the submitted files
            if 'category_image' in request.FILES:
                # Remove the existing category image file if it exists
                if category.category_image:
                    os.remove(category.category_image.path)
                
                # Save the new category image from the form submission
                category.category_image = request.FILES['category_image']

            # Update other category attributes from the form submission
            category.category_name = request.POST['category_name']
            category.category_description = request.POST['category_description']

            # Check if 'category_offer' exists in the form submission
            if 'category_offer' in request.POST:
                category_offer = int(request.POST['category_offer'])
                category.offer = category_offer
                
            # Save the updated category to the database
            category.save()

            # Display a success message and redirect to the admin category page
            messages.success(request, "Category Updated!")
            return redirect('admin_category')

        # Render the template for editing the category
        return render(request, 'admin/admin_edit_category.html', context)
    
    except Exception as e:
        # If an exception occurs, print it and redirect to the admin category page
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
    

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_control_category(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         category = Category.objects.get(id=id)
#         if category.is_active:
#             category.is_active = False
#             category.save()
#             messages.success(request, "Category unlisted!")
#         else:
#             category.is_active = True
#             category.save()
#             messages.success(request, "Category listed!")

#     except Exception as e:
#         print(e)

#     return redirect('admin_category')


@staff_member_required(login_url='admin_login')
def admin_control_category(request, id):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Retrieve the category with the specified id
        category = Category.objects.get(id=id)

        # Toggle the 'is_active' status of the category
        if category.is_active:
            category.is_active = False
            messages.success(request, "Category unlisted!")
        else:
            category.is_active = True
            messages.success(request, "Category listed!")

        # Save the updated 'is_active' status to the database
        category.save()

    except Exception as e:

        return render(request,'error_404.html')

    # Redirect to the admin category page
    return redirect('admin_category')


# @staff_member_required(login_url='admin_login')
# def admin_brands(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     context = {}

#     brands = ProductBrand.objects.all()
#     context = {
#         'brands' : brands
#     }

#     return render(request, 'admin/admin_brands.html', context)


@staff_member_required(login_url='admin_login')
def admin_brands(request):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Retrieve all ProductBrand objects from the database
        brands = ProductBrand.objects.all()

        # Prepare the context with the brands data
        context = {
            'brands': brands
        }

    except Exception as e:

        return render(request,'error_404.html')

    # Render the template with the brands data
    return render(request, 'admin/admin_brands.html', context)


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_add_brand(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     if request.method == 'POST':
#         brand_name = request.POST['brand_name']
#         brand_description = request.POST['brand_description']

#         # Check if a brand with the same name already exists
#         existing_brand = ProductBrand.objects.filter(brand_name=brand_name).first()

#         if existing_brand:
#             # Update the existing brand's description and image if provided
#             existing_brand.brand_description = brand_description
            
#             if request.FILES:
#                 existing_brand.brand_image = request.FILES['brand_image']
                
#             existing_brand.save()
            
#             messages.success(request, "Brand updated successfully!")
#         else:
#             # Create a new brand only if it doesn't exist
#             brand = ProductBrand(
#                 brand_name=brand_name,
#                 brand_description=brand_description,
#             )
            
#             if request.FILES:
#                 brand.brand_image = request.FILES['brand_image']

#             brand.save()
#             messages.success(request, "Brand added successfully!")

#         return redirect('admin_brands')

#     return render(request, 'admin/admin_add_brand.html')


@staff_member_required(login_url='admin_login')
def admin_add_brand(request):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Handle form submission (POST request)
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

            # Redirect to the admin brands page
            return redirect('admin_brands')

    except Exception as e:
        # If an exception occurs, print the error message
        return render(request,'error_404.html')

    # Render the template for adding a brand
    return render(request, 'admin/admin_add_brand.html')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_edit_brand(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     try:
#         brand = ProductBrand.objects.get(id=id)

#         if request.method == 'POST':
#             brand_name = request.POST['brand_name']
#             brand.brand_name = brand_name
#             slug = brand_name.replace("-", " ")
#             brand.slug = slug
#             brand.brand_description = request.POST['brand_description']

#             if 'brand_image' in request.FILES:
#                 if brand.brand_image:
#                     os.remove(brand.brand_image.path)
#                 brand.brand_image = request.FILES['brand_image']

#             brand.save()
#             messages.success(request, "Brand updated")
#             return redirect('admin_brand')

#         context = {
#             'brand': brand,
#         }

#         return render(request, 'admin/admin_edit_brand.html', context)
    
#     except Exception as e:
#         print(e)
#         return redirect('admin_brands')


@staff_member_required(login_url='admin_login')
def admin_edit_brand(request, id):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Retrieve the brand with the specified id
        brand = ProductBrand.objects.get(id=id)

        # Handle form submission (POST request)
        if request.method == 'POST':
            brand_name = request.POST['brand_name']
            brand.brand_name = brand_name
            slug = brand_name.replace("-", " ")
            brand.slug = slug
            brand.brand_description = request.POST['brand_description']

            # Check if 'brand_image' is in the submitted files
            if 'brand_image' in request.FILES:
                # Remove the existing brand image file if it exists
                if brand.brand_image:
                    os.remove(brand.brand_image.path)
                # Save the new brand image from the form submission
                brand.brand_image = request.FILES['brand_image']

            # Save the updated brand to the database
            brand.save()

            # Display a success message and redirect to the admin brand page
            messages.success(request, "Brand updated")
            return redirect('admin_brand')

        # Prepare the context with the brand data
        context = {
            'brand': brand,
        }

        # Render the template for editing the brand
        return render(request, 'admin/admin_edit_brand.html', context)

    except Exception as e:
        # If an exception occurs, print the error message and redirect to the admin brands page
        print(e)
        return redirect('admin_brands')
    

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_delete_brand(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     try:
#         brand = ProductBrand.objects.get(id=id)
#         if brand:
#             brand.delete()
#             messages.success(request, "Brand deleted successfully!")
#             return redirect('admin_brands')
#     except ProductBrand.DoesNotExist:
#         messages.error(request, "Brand does not exist.")
#         return redirect('admin_brands')

# Brand delete logic view
# @staff_member_required(login_url='admin_login')
# def admin_delete_brand(request, id):
#     # Check if 'email' is not in the session, redirect to admin login
#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         # Attempt to retrieve the brand with the specified id
#         brand = ProductBrand.objects.get(id=id)

#         # Check if the brand exists
#         if brand:
#             # Delete the brand
#             brand.delete()
#             messages.success(request, "Brand deleted successfully!")
#         else:
#             # Display an error message if the brand does not exist
#             messages.error(request, "Brand does not exist.")

#     except ProductBrand.DoesNotExist:
#         # Handle the case where the brand does not exist
#         messages.error(request, "Brand does not exist.")

#     # Redirect to the admin brands page
#     return redirect('admin_brands')


@staff_member_required(login_url='admin_login')
def admin_control_brand(request, id):
    # Check if 'email' is not in the session, redirect to admin login
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        # Attempt to retrieve the brand with the specified id
        brand = ProductBrand.objects.get(id=id)

        # Check if the brand exists
        if brand:
            # Toggle the 'is_active' status of the brand
            if brand.is_active:
                brand.is_active = False
                messages.success(request, "Brand unlisted!")
            else:
                brand.is_active = True
                messages.success(request, "Brand listed!")

            # Save the updated 'is_active' status to the database
            brand.save()

        else:
            # Display an error message if the brand does not exist
            messages.error(request, "Brand not found.")

    except Exception as e:

        return render(request,'error_404.html')

    # Redirect to the admin brands page
    return redirect('admin_brands')
    

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_control_brand(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     try:
#         brand = ProductBrand.objects.get(id=id)
#         if brand.is_active:
#             brand.is_active = False
#             messages.success(request, "Brand unlisted!")
#         else:
#             brand.is_active = True
#             messages.success(request, "Brand listed!")
#         brand.save()
#     except ProductBrand.DoesNotExist:
#         messages.error(request, "Brand not found.")
#     except Exception as e:
#         print(e)
#         messages.error(request, "An error occurred.")

#     return redirect('admin_brands')


# @staff_member_required(login_url='admin_login')
# def admin_products(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     context = {}

#     try:
#         products = Product.objects.all().order_by('-id')
#         context = {
#             'products' : products
#         }

#     except Exception as e:
#         print(e)

#     return render(request, 'admin/admin_products.html', context)

# ertet
# @staff_member_required(login_url='admin_login')
# def admin_products(request):
#     # Check if 'email' is not in the session, redirect to admin login
#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         # Retrieve all products and order them by ID in descending order
#         products = Product.objects.all().order_by('-id')

#         # Prepare the context with the products data
#         context = {
#             'products': products
#         }

#     except Exception as e:
#         # Log the exception or handle it appropriately
#         print(e)

#         # Return an error response or redirect to an error page
#         return render(request, 'error_404.html')

#     # Render the template with the products data
#     return render(request, 'admin/admin_products.html', context)

# fdsgreg
# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_add_product(request):
#     if 'email' not in request.session:
#         return redirect('admin_login')

#     categories = Category.objects.all()
#     brands = ProductBrand.objects.all()

#     context = {
#         'categories': categories,
#         'brands': brands,
#     }

#     try:
#         if request.method == 'POST':
#             product = Product()

#             # Extract form data
#             category_id = request.POST['category']
#             brand_id = request.POST['brand']
#             original_price = int(request.POST['original_price'])
#             selling_price = int(request.POST['selling_price'])
#             product_name = request.POST['product_name']
#             product_description = request.POST['product_description']
#             product_category_offer = 0
#             product_offer = 0

#             # Get the category offer
#             try:
#                 category = Category.objects.get(id=category_id)
#                 product_category_offer = category.offer
#             except Category.DoesNotExist:
#                 pass

#             # Apply category offer
#             if product_category_offer > 0:
#                 offer_amount = (original_price * product_category_offer) // 100
#                 if (original_price - offer_amount) < selling_price:
#                     selling_price -= offer_amount  # Deduct category offer

#             # Apply product offer (if needed)
#             product_offer = int(request.POST.get('product_offer', 0))
#             if product_offer > 0:
#                 product_offer_amount = (original_price * product_offer) // 100
#                 if (original_price - product_offer_amount) < selling_price:
#                     selling_price -= product_offer_amount  # Deduct product offer

#             # Save product details
#             product.product_name = product_name
#             product.slug = product_name.replace(" ", "-")
#             product.category = Category.objects.get(id=category_id)
#             product.brand = ProductBrand.objects.get(id=brand_id)
#             product.original_price = original_price
#             product.selling_price = selling_price
#             product.product_description = product_description
#             product.save()

#             # Save single product image
#             try:
#                 product_image = request.FILES.get('product_image', None)
#                 if product_image:
#                     product.product_image = product_image
#                     product.save()
#             except Exception as e:
#                 print(e)

#             # Save multiple product images
#             try:
#                 multiple_images = request.FILES.getlist('multiple_images', None)
#                 if multiple_images:
#                     for image in multiple_images:
#                         photo = MultipleImages.objects.create(
#                             product=product,
#                             images=image,
#                         )
#                         photo.save()
#             except Exception as e:
#                 print(e)

#             # Display success message and redirect
#             messages.success(request, "Product Created Successfully!")
#             return redirect('admin_products')

#     except Exception as e:
#         messages.error(request, "Product is already exist!")
#         print(e)

#     return render(request, 'admin/admin_add_product.html', context)

# reatfger
# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_edit_product(request, id):
#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         # Fetch existing product and related data
#         product = Product.objects.get(id=id)
#         product_category_offer = 0
#         product_offer = 0
#         multiple_images = MultipleImages.objects.filter(product=id)
#         brands = ProductBrand.objects.all()
#         categories = Category.objects.all()

#         context = {
#             'product': product,
#             'categories': categories,
#             'brands': brands,
#             'product_category_offer': product_category_offer,
#             'product_offer': product_offer,
#             'multiple_images': multiple_images,
#         }

#         if request.method == 'POST':
#             # Extract form data
#             original_price = float(request.POST.get('original_price'))
#             selling_price = float(request.POST.get('selling_price'))
#             product_offer = int(request.POST.get('product_offer', 0))

#             # Get the category offer
#             try:
#                 product_category_offer = product.category.offer
#             except Category.DoesNotExist:
#                 pass

#             # Apply category offer
#             if product_category_offer > 0:
#                 offer_amount = (original_price * product_category_offer) // 100
#                 selling_price -= offer_amount  # Deduct category offer

#             # Apply product offer (if needed)
#             if product_offer > 0:
#                 product_offer_amount = (original_price * product_offer) // 100
#                 selling_price -= product_offer_amount  # Deduct product offer

#             # Handle single image update
#             single_image = request.FILES.get('product_image', None)
#             if single_image:
#                 if product.product_image:
#                     product.product_image.delete()
#                 product.product_image = single_image

#             # Handle multiple images update
#             multiple_images = request.FILES.getlist('multiple_images')
#             # Clear existing multiple images for the product
#             MultipleImages.objects.filter(product=product).delete()
#             # Add new multiple images
#             for image in multiple_images:
#                 MultipleImages.objects.create(product=product, images=image)

#             # Update the product's category if it has changed
#             category_id = request.POST.get('category')
#             if category_id:
#                 new_category = Category.objects.get(id=category_id)
#                 product.category = new_category

#             # Update the product's brand if it has changed
#             brand_id = request.POST.get('brand')
#             if brand_id:
#                 new_brand = ProductBrand.objects.get(id=brand_id)
#                 product.brand = new_brand

#             # Update other product details
#             product.original_price = original_price
#             product.selling_price = selling_price
#             product.product_description = request.POST['product_description']

#             product.save()
#             messages.success(request, "Product updated successfully")
#             return redirect('admin_products')

#     except Product.DoesNotExist:
#         messages.error(request, "Product does not exist")
#         return redirect('admin_products')

#     except Exception as e:
#         print(e)

#     return render(request, 'admin/admin_edit_product.html', context)



@staff_member_required(login_url='admin_login')
def admin_products(request):

    if 'email' not in request.session:
        return redirect('admin_login')

    context = {}

    try:
        products = Product.objects.all().order_by('-id')
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
            category_id = request.POST['category']
            brand_id = request.POST['brand']
            original_price = int(request.POST['original_price'])
            selling_price = int(request.POST['selling_price'])
            product_category_offer = 0
            product_offer = 0

            # Get the category offer
            try:
                category = Category.objects.get(id=category_id)
                product_category_offer = category.offer
            except Category.DoesNotExist:
                pass

            # Apply category offer
            if product_category_offer > 0:
                offer_amount = (original_price * product_category_offer) // 100
                if (original_price - offer_amount) < selling_price:
                    selling_price -= offer_amount  # Deduct category offer

            # Apply product offer (if needed)
            product_offer = int(request.POST.get('product_offer', 0))
            if product_offer > 0:
                product_offer_amount = (original_price * product_offer) // 100
                if (original_price - product_offer_amount) < selling_price:
                    selling_price -= product_offer_amount  # Deduct product offer

            product_name = request.POST['product_name']
            product.product_name = product_name
            product_slug = product_name.replace(" ", "-")
            product.slug = product_slug
            product.category = Category.objects.get(id=category_id)
            product.brand = ProductBrand.objects.get(id=brand_id)
            product.original_price = original_price
            product.selling_price = selling_price
            product.product_description = request.POST['product_description']
            product.save()

            # Single image fetching
            try:
                product_image = request.FILES.get('product_image', None)
                if product_image:
                    product.product_image = product_image
                    product.save()
            except Exception as e:
                print(e)

            # Multiple image fetching
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
    product_category_offer = 0
    product_offer = 0
    multiple_images = MultipleImages.objects.filter(product=id)
    brands = ProductBrand.objects.all()
    categories = Category.objects.all()

    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
        'product_category_offer': product_category_offer,
        'product_offer': product_offer,
        'multiple_images': multiple_images,
    }

    try:
        if request.method == 'POST':
            original_price = float(request.POST.get('original_price'))
            selling_price = float(request.POST.get('selling_price'))
            product_offer = int(request.POST.get('product_offer', 0))

            # Get the category offer
            try:
                product_category_offer = product.category.offer
            except Category.DoesNotExist:
                pass

            # Apply category offer
            if product_category_offer > 0:
                offer_amount = (original_price * product_category_offer) // 100
                selling_price -= offer_amount  # Deduct category offer

            # Apply product offer (if needed)
            if product_offer > 0:
                product_offer_amount = (original_price * product_offer) // 100
                selling_price -= product_offer_amount  # Deduct product offer

            single_image = request.FILES.get('product_image', None)

            multiple_images = request.FILES.getlist('multiple_images')
            # Clear existing multiple images for the product
            MultipleImages.objects.filter(product=product).delete()

            # Add new multiple images
            for image in multiple_images:
                MultipleImages.objects.create(product=product, images=image)

            # Update the product's category if it has changed
            category_id = request.POST.get('category')
            if category_id:
                new_category = Category.objects.get(id=category_id)
                product.category = new_category

            # Update the product's brand if it has changed
            brand_id = request.POST.get('brand')
            if brand_id:
                new_brand = ProductBrand.objects.get(id=brand_id)
                product.brand = new_brand

            product.original_price = original_price
            product.selling_price = selling_price
            product.product_description = request.POST['product_description']

            if single_image:
                if product.product_image:
                    product.product_image.delete()
                product.product_image = single_image

            product.save()
            messages.success(request, "Product updated successfully!")
            return redirect('admin_products')
    except Exception as e:
        print(e)

    return render(request, 'admin/admin_edit_product.html', context)



# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_add_product(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     categories = Category.objects.all()
#     brands = ProductBrand.objects.all()

#     context = {
#         'categories': categories,
#         'brands': brands,
#     }

#     try:
#         if request.method == 'POST':
#             product = Product()
#             category_id = request.POST['category']
#             brand_id = request.POST['brand']
#             original_price = int(request.POST['original_price'])
#             selling_price = int(request.POST['selling_price'])
#             product_category_offer = 0
#             product_offer = 0

#             # Get the category offer
#             try:
#                 category = Category.objects.get(id=category_id)
#                 product_category_offer = category.offer
#             except Category.DoesNotExist:
#                 pass

#             # Apply category offer
#             if product_category_offer > 0:
#                 offer_amount = (original_price * product_category_offer) // 100
#                 if (original_price - offer_amount) < selling_price:
#                     selling_price -= offer_amount  # Deduct category offer

#             # Apply product offer (if needed)
#             product_offer = int(request.POST.get('product_offer', 0))
#             if product_offer > 0:
#                 product_offer_amount = (original_price * product_offer) // 100
#                 if (original_price - product_offer_amount) < selling_price:
#                     selling_price -= product_offer_amount  # Deduct product offer

#             product_name = request.POST['product_name']
#             product.product_name = product_name
#             product_slug = product_name.replace(" ", "-")
#             product.slug = product_slug
#             product.category = Category.objects.get(id=category_id)
#             product.brand = ProductBrand.objects.get(id=brand_id)
#             product.original_price = original_price
#             product.selling_price = selling_price
#             product.product_description = request.POST['product_description']
#             product.save()

#             # Single image fetching
#             try:
#                 product_image = request.FILES.get('product_image', None)
#                 if product_image:
#                     product.product_image = product_image
#                     product.save()
#             except Exception as e:
#                 print(e)

#             # Multiple image fetching
#             try:
#                 multiple_images = request.FILES.getlist('multiple_images', None)
#                 if multiple_images:
#                     for image in multiple_images:
#                         photo = MultipleImages.objects.create(
#                             product=product,
#                             images=image,
#                         )
#                         photo.save()
#             except Exception as e:
#                 print(e)

#             messages.success(request, "Product Created Successfully!")

#             return redirect('admin_products')
        
#     except Exception as e:
#         messages.error(request, "Product is already exist!")
#         print(e)

#     return render(request, 'admin/admin_add_product.html', context)


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_edit_product(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     product = Product.objects.get(id=id)
#     product_category_offer = 0
#     product_offer = 0
#     multiple_images = MultipleImages.objects.filter(product=id)
#     brands = ProductBrand.objects.all()
#     categories = Category.objects.all()

#     context = {
#         'product': product,
#         'categories': categories,
#         'brands': brands,
#         'product_category_offer': product_category_offer,
#         'product_offer': product_offer,
#         'multiple_images': multiple_images,
#     }

#     try:
#         if request.method == 'POST':
#             original_price = float(request.POST.get('original_price'))
#             selling_price = float(request.POST.get('selling_price'))
#             product_offer = int(request.POST.get('product_offer', 0))

#             # Get the category offer
#             try:
#                 product_category_offer = product.category.offer
#             except Category.DoesNotExist:
#                 pass

#             # Apply category offer
#             if product_category_offer > 0:
#                 offer_amount = (original_price * product_category_offer) // 100
#                 selling_price -= offer_amount  # Deduct category offer

#             # Apply product offer (if needed)
#             if product_offer > 0:
#                 product_offer_amount = (original_price * product_offer) // 100
#                 selling_price -= product_offer_amount  # Deduct product offer

#             single_image = request.FILES.get('product_image', None)

#             multiple_images = request.FILES.getlist('multiple_images')
#             # Clear existing multiple images for the product
#             MultipleImages.objects.filter(product=product).delete()

#             # Add new multiple images
#             for image in multiple_images:
#                 MultipleImages.objects.create(product=product, images=image)

#             # Update the product's category if it has changed
#             category_id = request.POST.get('category')
#             if category_id:
#                 new_category = Category.objects.get(id=category_id)
#                 product.category = new_category

#             # Update the product's brand if it has changed
#             brand_id = request.POST.get('brand')
#             if brand_id:
#                 new_brand = ProductBrand.objects.get(id=brand_id)
#                 product.brand = new_brand

#             product.original_price = original_price
#             product.selling_price = selling_price
#             product.product_description = request.POST['product_description']

#             if single_image:
#                 if product.product_image:
#                     product.product_image.delete()
#                 product.product_image = single_image

#             product.save()
#             messages.success(request, "Product updated successfully!")
#             return redirect('admin_products')
#     except Exception as e:
#         print(e)

#     return render(request, 'admin/admin_edit_product.html', context)


# Delete product logic view
# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_delete_product(request, id):
#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         product = Product.objects.get(id=id)

#         # Remove the product image file if it exists
#         if product.product_image:
#             if len(product.product_image) != 0:
#                 os.remove(product.product_image.path)

#         # Delete the product
#         product.delete()
#         messages.success(request, "Product deleted successfully!")

#     except Product.DoesNotExist:
#         raise Http404("Product does not exist.")

#     except Exception as e:
#         return render(request,'error_404.html')

#     return redirect('admin_products')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_control_product(request, id):
    if 'email' not in request.session:
        return redirect('admin_login')

    try:
        product = Product.objects.get(id=id)

        # Toggle the product's availability status
        if product.is_available:
            product.is_available = False
            messages.success(request, "Product unlisted!")
        else:
            product.is_available = True
            messages.success(request, "Product listed!")

        product.save()

    except Product.DoesNotExist:
        raise Http404("Product does not exist.")

    except Exception as e:
        return render(request,'error_404.html')

    return redirect('admin_products')

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_delete_product(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     product = Product.objects.get(id=id)
#     if product.product_image:
#         if len(product.product_image) != 0:
#             os.remove(product.product_image.path)
#     product.delete()
#     messages.success(request, "Product deleted successfully!")

#     return redirect('admin_products')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_control_product(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         product = Product.objects.get(id=id)
#         if product.is_available:
#             product.is_available = False
#             messages.success(request, "Product unlisted!")
#         else:
#             product.is_available = True
#             messages.success(request, "Product listed!")
#         product.save()

#     except Exception as e:
#         print(e)
#     return redirect('admin_products')


# @staff_member_required(login_url='admin_login')
# def admin_product_variant(request, product_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     context = {}

#     variant = ProductVariant.objects.filter(product=product_id)

#     context = {
#         'variants' : variant,
#         'product_id' : product_id,
#     }

#     return render(request, 'admin/admin_product_variant.html',context)


@staff_member_required(login_url='admin_login')
def admin_product_variant(request, product_id):
    # Check if the user is a staff member (admin)
    if 'email' not in request.session:
        return redirect('admin_login')

    # Retrieve the variants for the specified product
    variants = ProductVariant.objects.filter(product=product_id)

    # Prepare the context with the variants and product_id
    context = {
        'variants': variants,
        'product_id': product_id,
    }

    # Render the admin_product_variant.html template with the context
    return render(request, 'admin/admin_product_variant.html', context)


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_product_variant(request, product_id):
    try:
        # Check if the user is authenticated as a staff member
        if 'email' not in request.session:
            return redirect('admin_login')

        context = {}
        product = Product.objects.get(id=product_id)
        product_variants = ProductVariant.objects.filter(product=product)
        sizes = ProductSize.objects.all().order_by('id')

        # Handle the form submission
        if request.method == 'POST':
            size_id = request.POST['size']
            stock = request.POST['stock']
            variant_size = ProductSize.objects.get(id=size_id)

            try:
                variant = ProductVariant.objects.get(product=product_id, product_size=variant_size)

                # If the variant already exists, update the stock
                if variant:
                    print("Existing variant")
                    variant.stock = variant.stock + int(stock)
            except ProductVariant.DoesNotExist:
                # If the variant doesn't exist, create a new one
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

    except Exception as e:
        # Handle exceptions, log, or redirect as needed
        print(e)
        return render(request, 'error_404.html')


# Admin view to edit a product variant
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_product_variant(request, variant_id):
    try:
        # Check if the user is authenticated as a staff member
        if 'email' not in request.session:
            return redirect('admin_login')

        # Handle the form submission
        if request.method == 'POST':
            stock = request.POST['stock']
            variant = get_object_or_404(ProductVariant, id=variant_id)
            variant.stock = stock
            variant.save()
            messages.success(request, 'Stock updated successfully')

        return redirect('admin_product_variant', variant.product.id)

    except ProductVariant.DoesNotExist:
        # Handle the case where the variant does not exist
        messages.error(request, 'Product variant not found')
        return redirect('admin_product_variant')
    except Exception as e:
        # Handle other exceptions, log, or redirect as needed
        print(e)
        return render(request, 'error_404.html')
    

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_add_product_variant(request,product_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     context = {}

#     product = Product.objects.get(id=product_id)
#     product_variants = ProductVariant.objects.filter(product=product)
#     sizes = ProductSize.objects.all().order_by('id')

#     if request.method == 'POST':
#         size_id = request.POST['size']
#         stock = request.POST['stock']
#         variant_size = ProductSize.objects.get(id=size_id)

#         try:
#             variant = ProductVariant.objects.get(product=product_id, product_size=variant_size)

#             if variant:
#                 print("Existing variant")
#                 variant.stock = variant.stock + int(stock)
#         except:
#             variant = ProductVariant.objects.create(
#                 product=product,
#                 product_size=variant_size,
#                 stock=stock,
#             )
#         return redirect('admin_product_variant', product_id)

#     context = {
#         'product': product,
#         'sizes': sizes,
#         'product_variants': product_variants,
#     }
#     return render(request, 'admin/admin_add_product_variant.html', context)


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_edit_product_variant(request, variant_id):
#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         if request.method == 'POST':
#             stock = request.POST['stock']
#             variant = get_object_or_404(ProductVariant, id=variant_id)
#             variant.stock = stock
#             variant.save()
#             messages.success(request, 'Stock updated successfully')

#         return redirect('admin_product_variant', variant.product.id)

#     except ProductVariant.DoesNotExist:
#         messages.error(request, 'Product variant not found')

#     return redirect('admin_product_variant')

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_product_variant(request, variant_id):
    try:
        # Check if the user is authenticated as a staff member
        if 'email' not in request.session:
            return redirect('admin_login')

        # Get the product variant and its associated product
        variant = ProductVariant.objects.get(id=variant_id)
        product = variant.product

        if variant:
            # Delete the variant and redirect to the product's variants page
            variant.delete()
            return redirect('admin_product_variant', product.id)

    except ProductVariant.DoesNotExist:
        # Handle the case where the variant does not exist
        pass
    except Exception as e:
        # Handle other exceptions, log, or redirect as needed
        print(e)

    return redirect('admin_dashboard')


# Admin view to control the status of a product variant (active or inactive)
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_control_product_variant(request, variant_id):
    try:
        # Check if the user is authenticated as a staff member
        if 'email' not in request.session:
            return redirect('admin_login')

        # Get the product variant and its associated product ID
        variant = ProductVariant.objects.get(id=variant_id)
        product_id = variant.product.id

        # Toggle the is_active status of the variant
        if variant.is_active:
            variant.is_active = False
        else:
            variant.is_active = True
        variant.save()

        # Redirect to the product's variants page
        return redirect('admin_product_variant', product_id)

    except ProductVariant.DoesNotExist:
        # Handle the case where the variant does not exist
        pass
    except Exception as e:
        # Handle other exceptions, log, or redirect as needed
        print(e)
        return redirect('admin_products')
    

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_delete_product_variant(request, variant_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         variant = ProductVariant.objects.get(id=variant_id)
#         product = variant.product
        
#         if variant:
#             variant.delete()
            
#             return redirect('admin_product_variant', product.id)
        
#     except Exception as e:
#         print(e)

#     return redirect('admin_dashboard')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_control_product_variant(request, variant_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         variant = ProductVariant.objects.get(id=variant_id)
#         product_id = variant.product.id
#         if variant.is_active:
#             variant.is_active = False
#         else:
#             variant.is_active = True
#         variant.save()
#         return redirect('admin_product_variant', product_id)
#     except Exception as e:
#         print(e)
#         return redirect('admin_products')
    

# @staff_member_required(login_url='admin_login')
# def admin_coupons(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     context = {}
#     try:
#         coupons = Coupons.objects.all().order_by('-id') 
#         context = {
#             'coupons': coupons,
#         }
#         return render(request, 'admin/admin_coupons.html', context)

#     except Exception as e:
#         print(e)
#         return render(request, 'admin/admin_coupons.html')


# @staff_member_required(login_url='admin_login')
# def admin_coupons(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         coupons = Coupons.objects.all().order_by('-id') 
#         context = {
#             'coupons': coupons,
#         }
#         return render(request, 'admin/admin_coupons.html', context)

#     except Exception as e:
#         print(e)
#         return render(request, 'admin/admin_coupons.html')
    

@staff_member_required(login_url='admin_login')
def admin_coupons(request):
    try:
        # Check if the user is authenticated as a staff member
        if 'email' not in request.session:
            return redirect('admin_login')

        # Get all coupons and order them by ID in descending order
        coupons = Coupons.objects.all().order_by('-id') 

        # Prepare the context to be passed to the template
        context = {
            'coupons': coupons,
        }

        # Render the admin coupons page with the context
        return render(request, 'admin/admin_coupons.html', context)

    except Exception as e:
        # Handle exceptions, log, or redirect as needed
        print(e)
        return render(request, 'admin/admin_coupons.html')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_add_coupon(request):

    try:
        if 'email' not in request.session:
            return redirect('admin_login')

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

    except Exception as e:
        return render(request, 'error_404.html')
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_edit_coupon(request, coupon_id):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')
        
        try:
            # Retrieve the coupon instance or return a 404 response
            coupon = get_object_or_404(Coupons, id=coupon_id)

            # Check if the request method is POST
            if request.method == "POST":
                # Extract data from the POST request
                coupon_code = request.POST.get("coupon_code", "").strip()
                new_discount = request.POST.get("discount", "0")

                discount = Decimal(new_discount)
                minimum_order_amount = int(request.POST.get("minimum_order_amount", "0"))

                # Validate coupon data
                if discount < 1:
                    messages.error(request, "Minimum discount amount should be 1")
                    return redirect("admin_coupons")

                if discount >= minimum_order_amount:
                    messages.error(request, "Discount has to be less than the minimum amount")
                    return redirect("admin_coupons")

                valid_from = request.POST.get("valid_from", "")
                valid_to = request.POST.get("valid_to", "")

                if valid_from > valid_to:
                    messages.error(request, "Add validity range properly")
                    return redirect("admin_coupons")

                # Update the coupon instance with new data
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

    except Exception as e:
        return render(request, 'error_404.html')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_add_coupon(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     if request.method == "POST":

#         try:
#             coupon_code = request.POST.get("coupon_code", "").strip()
#             discount = float(request.POST.get("discount", 0))
#             minimum_order_amount = float(request.POST.get("minimum_order_amount", 0))
#             valid_from = request.POST.get("valid_from", "")
#             valid_to = request.POST.get("valid_to", "")
#             description = request.POST.get("description", "") 

#             if discount < 1:
#                 messages.error(request, "The minimum discount amount should be 1.")
#             elif discount > minimum_order_amount:
#                 messages.error(request, "The discount must be less than the minimum order amount.")
#             elif valid_from > valid_to:
#                 messages.error(request, "Please ensure the validity range is correct.")
#             else:
#                 coupon = Coupons.objects.create(
#                     coupon_code=coupon_code,
#                     discount=discount,
#                     minimum_order_amount=minimum_order_amount,
#                     valid_from=valid_from,
#                     valid_to=valid_to,
#                     description=description 
#                 )
#                 coupon.save()
#                 messages.success(request, "New coupon added successfully.")
#                 return redirect("admin_coupons")

#         except ValidationError as e:
#             messages.error(request, f"Validation Error: {e}")
#         except Exception as e:
#             print(e) 

#     return render(request, 'admin/admin_add_coupon.html')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_edit_coupon(request, coupon_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     try:
#         coupon = get_object_or_404(Coupons, id=coupon_id)

#         if request.method == "POST":

#             coupon_code = request.POST.get("coupon_code", "").strip()
#             new_discount = request.POST.get("discount", "0")

#             discount = Decimal(new_discount)
#             minimum_order_amount = int(request.POST.get("minimum_order_amount", "0"))

#             if discount < 1:
#                 messages.error(request, "Minimum discount amount should be 1")
#                 return redirect("admin_coupons")

#             if discount >= minimum_order_amount:
#                 messages.error(request, "Discount has to be less than minimum amount")
#                 return redirect("admin_coupons")

#             valid_from = request.POST.get("valid_from", "")
#             valid_to = request.POST.get("valid_to", "")

#             if valid_from > valid_to:
#                 messages.error(request, "Add validity range properly")
#                 return redirect("admin_coupons")

#             coupon.coupon_code = coupon_code
#             coupon.discount = discount
#             coupon.minimum_order_amount = minimum_order_amount
#             coupon.valid_from = valid_from
#             coupon.valid_to = valid_to
#             coupon.save()
#             messages.success(request, "Coupon updated successfully!")
#             return redirect("admin_coupons")


#     except Coupons.DoesNotExist:
#         messages.error(request, "Coupon not found")
#         return redirect("admin_coupons")
#     except Exception as e:
#         messages.error(request, f"An error occurred: {str(e)}")

#     return render(request, 'admin/admin_edit_coupon.html')


# admin_delete_coupon view
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_delete_coupon(request, coupon_id):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')
        
        # Retrieve the coupon instance or return a 404 response
        coupon = get_object_or_404(Coupons, id=coupon_id)
        
        # Delete the coupon instance
        coupon.delete()
        messages.success(request, "Coupon deleted successfully")
    
    except Coupons.DoesNotExist as e:
        # Handle the case where the coupon does not exist
        messages.error(request, "Coupon not found")
    
    except Exception as e:
        # Handle other exceptions, log, or redirect as needed
        messages.error(request, "An error occurred while deleting the coupon")
    
    return redirect('admin_coupons')


# admin_activate_coupon view
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_activate_coupon(request, coupon_id):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')
        
        # Retrieve the coupon instance or return a 404 response
        coupon = Coupons.objects.get(id=coupon_id)
        
        # Toggle the active status of the coupon
        if coupon.active:
            coupon.active = False
            messages.success(request, "Coupon deactivated")
        else:
            coupon.active = True
            messages.success(request, "Coupon activated")
        
        coupon.save()
    
    except Exception as e:
        # Log the exception or handle it appropriately
        print(e)
    
    return redirect('admin_coupons')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_delete_coupon(request, coupon_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     try:
#         coupon = get_object_or_404(Coupons, id=coupon_id)
#         coupon.delete()
#         messages.success(request, "Coupon deleted succcessfully")
#     except Coupons.DoesNotExist as e:
#         messages.error(request, "Coupon not found")
#     except Exception as e:
#         messages.error(request, "An error occurred while deleting the coupon")
#     return redirect('admin_coupons')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_activate_coupon(request, coupon_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     try:
#         coupon = Coupons.objects.get(id=coupon_id)
#         if coupon.active:
#             coupon.active = False
#             messages.success(request, "Coupon deactivated")
#         else:
#             coupon.active = True
#             messages.success(request, "Coupon activated")
#         coupon.save()
#     except Exception as e:
#         print(e)
#     return redirect('admin_coupons')


# @staff_member_required(login_url='admin_login')
# def admin_orders(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     context = {}
#     try:
#         orders = Order.objects.all().order_by('-order_id')
#         context = {
#             'orders': orders,
#     }
#     except Exception as e:
#         return render(request,'error_404.html')
    
#     return render(request, 'admin/admin_orders.html', context)


@staff_member_required(login_url='admin_login')
def admin_orders(request):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')
        
        # Retrieve all orders and order them by order_id in descending order
        orders = Order.objects.all().order_by('-order_id')
        
        # Prepare the context to be passed to the template
        context = {
            'orders': orders,
        }
    
    except Exception as e:
        # Log the exception or handle it appropriately
        return render(request, 'error_404.html')
    
    # Render the admin_orders template with the context
    return render(request, 'admin/admin_orders.html', context)


@staff_member_required(login_url="admin_login")
def admin_orders_detail(request, id):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')

        # Retrieve the order with the specified id
        order = Order.objects.get(id=id)
        
        # Retrieve order items related to the order
        order_items = OrderProduct.objects.filter(order_id=order)

        # Prepare the context to be passed to the template
        context = {
            "order": order,
            "order_items": order_items,
        }
    
    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        return render(request, 'error_404.html')
    except Exception as e:
        # Log the exception or handle it appropriately
        return render(request, 'error_404.html')

    # Render the admin_orders_detail template with the context
    return render(request, "admin/admin_orders_detail.html", context)


# @staff_member_required(login_url="admin_login")
# def admin_orders_detail(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     order = Order.objects.get(id=id)
    
#     order_items = OrderProduct.objects.filter(order_id=order)
#     context = {
#         "order": order,
#         "order_items": order_items,
#     }
#     return render(request, "admin/admin_orders_detail.html", context)


# @staff_member_required(login_url="admin_login")
# def admin_orders_status(request, id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     if request.method == 'POST':

#         new_status = request.POST.get('new_status')
#         order = Order.objects.get(id=id)
#         order.status = new_status
#         order.save()

#     return redirect('admin_orders')


# admin_orders_status view
@staff_member_required(login_url="admin_login")
def admin_orders_status(request, id):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')

        # Check if the request method is POST
        if request.method == 'POST':
            # Get the new status from the POST data
            new_status = request.POST.get('new_status')

            # Retrieve the order with the specified id
            order = Order.objects.get(id=id)

            # Update the order status with the new status
            order.status = new_status
            order.save()

        # Redirect to the admin_orders view
        return redirect('admin_orders')

    except Order.DoesNotExist:
        # Handle the case where the order does not exist
        return render(request, 'error_404.html')
    except Exception as e:
        # Log the exception or handle it appropriately
        return render(request, 'error_404.html')


# @staff_member_required(login_url="admin_login")
# def admin_banner(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     context = {}
#     try:
#         banners = Banner.objects.all().order_by('id')
#         context = {
#             "banners": banners,
#         }
#         return render(request, "admin/admin_banner.html", context)

#     except Exception as e:
#         print(e)
#         return render(request, "admin/admin_banner.html", context)
    

# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url="admin_login")
# def admin_edit_banner(request, banner_id):

#     if 'email' not in request.session:
#         return redirect('admin_login')

#     try:
#         banner = get_object_or_404(Banner, id=banner_id)

#         if request.method == "POST":
#             name = request.POST.get("name")  
#             image = request.FILES.get("image") 

#             if name:
#                 banner.name = name

#             if image:
#                 banner.image = image

#             banner.save()
#             messages.success(request, "Banner Updated Successfully")
#             return redirect("admin_banner")

#         # Render the form for GET requests
#         return render(request, "admin/admin_edit_banner.html", {'banner': banner})

#     except Exception as e:
#         print(e)
#         messages.error(request, "Failed to update the banner.")
#         return redirect("admin_banner")


# admin_banner view
@staff_member_required(login_url="admin_login")
def admin_banner(request):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')

        # Retrieve all banners and order them by id
        banners = Banner.objects.all().order_by('id')

        # Prepare the context to be passed to the template
        context = {
            "banners": banners,
        }

        # Render the admin_banner page with the context
        return render(request, "admin/admin_banner.html", context)

    except Exception as e:
        # Log the exception or handle it appropriately
        print(e)
        # Render the admin_banner page with an empty context or handle it appropriately
        return render(request, "admin/admin_banner.html", context)


# admin_edit_banner view
@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url="admin_login")
def admin_edit_banner(request, banner_id):
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            return redirect('admin_login')

        # Retrieve the banner with the specified id
        banner = get_object_or_404(Banner, id=banner_id)

        # Check if the request method is POST
        if request.method == "POST":
            # Get the name and image from the POST data
            name = request.POST.get("name")
            image = request.FILES.get("image")

            # Update the banner fields if they are provided in the POST data
            if name:
                banner.name = name
            if image:
                banner.image = image

            # Save the changes to the banner
            banner.save()

            # Display a success message and redirect to admin_banner view
            messages.success(request, "Banner Updated Successfully")
            return redirect("admin_banner")

        # Render the form for GET requests
        return render(request, "admin/admin_edit_banner.html", {'banner': banner})

    except Exception as e:
        # Log the exception or handle it appropriately
        print(e)
        # Display an error message and redirect to admin_banner view
        messages.error(request, "Failed to update the banner.")
        return redirect("admin_banner")
    

@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def admin_logout(request):

    if 'email' not in request.session:
        return redirect('admin_login')
    
    logout(request)
    request.session.flush()
    return redirect('admin_login')


# @cache_control(no_cache=True, no_store=True)
# @staff_member_required(login_url='admin_login')
# def admin_logout(request):

#     if 'email' not in request.session:
#         return redirect('admin_login')
    
#     logout(request)
#     request.session.flush()
#     return redirect('admin_login')


@cache_control(no_cache=True, no_store=True)
@staff_member_required(login_url='admin_login')
def error_404(request):

    return render(request, 'error_404.html')