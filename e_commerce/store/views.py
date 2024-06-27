from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
import json
import secrets
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, UserForm
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

# Create your views here.

def store(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    products = Product.objects.filter(
        Q(name__icontains=q) |
        Q(price__icontains=q)
    )
    items_per_page = 6
    paginator = Paginator(products,items_per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if request.user.is_authenticated:
        customer = request.user.customer 
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartitems= order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, "get_cart_items":0, 'shipping':False}
        cartitems = order['get_cart_items']
    return render(request, 'store/store.html', context={'products':products, 
                                                        'cartitems':cartitems,
                                                        'page_obj':page_obj,})

@login_required(login_url='loginpage')
def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer 
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartitems= order.get_cart_items
    return render(request, 'store/checkout.html', context={'items':items,'order':order, 'cartitems':cartitems})

@login_required(login_url='loginpage')
def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer 
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartitems= order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, "get_cart_items":0, 'shipping':False}
        cartitems = order['get_cart_items']
    return render(request, 'store/cart.html', context={'items':items,'order':order, 'cartitems':cartitems})

@login_required(login_url='loginpage')
def update_item(request):
    data = json.loads(request.body)
    productID = data['productId']
    action = data['action']
    # print('Action', action)
    # print('productID', productID)
    customer = request.user.customer
    product = Product.objects.get(id=productID)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)
    
    if action == 'add':
        orderitem.quantity = (orderitem.quantity + 1)
        messages.info(request,'An item added to your cart')
    elif action == 'remove':
        orderitem.quantity = (orderitem.quantity - 1)
        messages.info(request,'An item removed from your cart')
    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()

    return JsonResponse('Item was added', safe=False)

@login_required(login_url='loginpage')
def process_order(request):
    transaction_id = secrets.randbelow(10**10)
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id= transaction_id
        items = OrderItem.objects.filter(order=order)
        # items = order.orderitem_set.all()
        
        if order.get_cart_total == total:
            order.complete = True
        order.save()

        if order.shipping == True:
            address= data['shipping']['address']
            city= data['shipping']['city']
            state= data['shipping']['state']
            zipcode= data ['shipping']['zipcode']
            country= data['shipping']['country']
            ShippingAddress.objects.create(customer=customer, 
                                           order=order,
                                           address= address,
                                           city= city,
                                           state= state,
                                           zipcode= zipcode,
                                           country= country
                                           )
            messages.success(request, 'Order Placed Successfully, please check your email for further updates!')
            send_mail(subject=f'Order details from Sand-Box Shopping',
                      message=f'''
Hi {request.user}:

    Thank you for your order! Below are the details of your purchase:
        
        Customer Name : {customer}
        Order ID: {order}
        Items : {[item.product.name for item in items]}
        transaction_id = {order.transaction_id}
        Address : {address}
        City : {city}
        State : {state}
        Zipcode : {zipcode}
        Country : {country}

*****We will notify you once your order is shipped*****

        Thank you for shopping with us!
        (Team Sand-Box Shopping)
''',
from_email=settings.DEFAULT_FROM_EMAIL,
recipient_list=[customer.email],
fail_silently=False)
    else:
        print('User not logged in')


    return JsonResponse('Payment complete', safe=False)


def login_view(request):

    if request.user.is_authenticated:
        return redirect('storepage')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"You've been successfully logged in")
            return redirect('storepage')
        else:
            messages.error(request,'Username or Password is Invalid')
    return render(request,'store/login.html', context={'page':'login_page'})

def register_view(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer = Customer.objects.create(user=user,name=request.POST.get('username'), email=request.POST.get('email'))
            login(request,user)
            messages.success(request,"Account Created Successfully!")
            return redirect('storepage')
        else:
            messages.error(request,'An error occured while creating your account!')
    return render(request,'store/login.html', context={'page':'register_page','form':form})

@login_required(login_url='loginpage')
def logout_view(request):
    logout(request)
    messages.success(request,"Logged out successfully!")
    return redirect('storepage')

@login_required(login_url='loginpage')
def update_profile(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            customer = Customer.objects.get(user=user)
            customer.name = request.POST.get('username')
            customer.email = request.POST.get('email')
            customer.save()
            messages.success(request,"Profile Updated Successfully!")
            return redirect('storepage')
        else:
            messages.error(request,"An error occured while updating your account")
    return render(request,'store/profile.html', context={'form':form})


def about_page(request):
    return render(request,'store/about.html')

def contact_page(request):
    return render(request,'store/contactus.html')

def feedback_page(request):
    if request.method =='POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        feedback = request.POST.get('feedback')
        send_mail(subject=f'Feedback from {name}',
                  message=f"""
Sender Mail {email}:

Feedback: {feedback}
""",
                  from_email=email,
                  recipient_list=[settings.DEFAULT_FROM_EMAIL],
                  fail_silently=False)
        messages.success(request,"Feedback sent successfully")
        return redirect('storepage')
    return render(request,'store/feedback.html')
