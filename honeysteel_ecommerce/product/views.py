from django.shortcuts import render,get_list_or_404,get_object_or_404,redirect
from .models import Product,Order
from customer.models import Customer
from django.contrib import messages
import threading
import time,random
from collections import defaultdict
from django.contrib.auth.models import User
from django.db import transaction
from datetime import datetime
from threading import Lock
from django.utils.timezone import now

product_locks = defaultdict(threading.Lock)

def calculate_priority(order):
    
    
    base_priority = 15 if order.customer.customer_type == "Premium" else 10
    wait_time = (now() - order.order_date).total_seconds()
    wait_time_weight = 0.5
    return base_priority + (wait_time * wait_time_weight)


def process_order(order):

    global product_locks


    product_lock = product_locks[order.product.product_id]

    with product_lock:  
        with transaction.atomic():  
            
            product = Product.objects.select_for_update().get(product_id=order.product.product_id)

           
            customer = order.customer.__class__.objects.select_for_update().get(pk=order.customer.pk)

            if order.quantity > product.stock:
                
                order.order_status = "CANCELLED"
                order.save()
                return

           
            product.stock -= order.quantity
            product.save()

       
            customer.budget -= order.total_price

    
            customer.total_spent += order.total_price

            
            if customer.total_spent > 2000:
                customer.customer_type = "Premium"

           
            customer.save()

            
            order.order_status = "COMPLETED"
            order.save()
        
        
def reset_db(request):
 
    Order.objects.all().delete()

    Product.objects.all().delete()


    Customer.objects.all().delete()
    User.objects.filter(is_superuser=False).delete() 

    
    predefined_products = [
        {"product_id": 1, "product_name": "Product1", "stock": 500, "price": 100},
        {"product_id": 2, "product_name": "Product2", "stock": 10, "price": 50},
        {"product_id": 3, "product_name": "Product3", "stock": 200, "price": 45},
        {"product_id": 4, "product_name": "Product4", "stock": 75, "price": 75},
        {"product_id": 5, "product_name": "Product5", "stock": 0, "price": 500},
    ]

    for product_data in predefined_products:
        Product.objects.create(
            product_id=product_data["product_id"],
            product_name=product_data["product_name"],
            stock=product_data["stock"],
            price=product_data["price"],
        )


    usernames = [f"user{i}" for i in range(1, 11)]  
    for i, username in enumerate(usernames):
        user = User.objects.create_user(username=username, password="password123")
        customer_type = "Premium" if i < 2 else "Normal"  
        Customer.objects.create(
            user=user,
            customer_name=username.capitalize(),
            budget=random.randint(500, 3000),
            customer_type=customer_type,
            total_spent=0,
        )

    messages.success(request, "Database reset successfully!")
    return redirect("administration:dashboard")  
        
def confirm_all_orders(request):
    if request.method == "GET":
    
        pending_orders = Order.objects.filter(order_status="PENDING")

        
        sorted_orders = sorted(pending_orders, key=calculate_priority, reverse=True)

        threads = []

        
        for order in sorted_orders:
            thread = threading.Thread(target=process_order, args=(order,))
            threads.append(thread)
            thread.start()

        
        for thread in threads:
            thread.join()

        messages.success(request, "All pending orders have been processed.")
        return redirect("administration:dashboard")

    messages.error(request, "Invalid request method.")
    return redirect("administration:dashboard")


def products(request):
    
    products = Product.objects.all()

    
    context = {'products': products}
    return render(request, 'product/products.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product_id = str(product_id)  

    if request.method == "POST":

        quantity = int(request.POST.get("quantity", 0))


        if quantity <= 0 or quantity > product.stock or quantity > 5:
            messages.error(request, "Invalid quantity. Check stock availability. (Max: 5 items)")
            return redirect('product:products')


        cart = request.session.get('cart', {})


        if product_id in cart:

            if cart[product_id] + quantity > 5:
                messages.error(request, "Cannot add more than 5 of this product to the cart.")
                return redirect('product:products')


            cart[product_id] += quantity
        else:

            cart[product_id] = quantity


        request.session['cart'] = cart
        request.session.modified = True

        messages.success(request, f"{quantity} x '{product.product_name}' added to cart.")
    else:
        messages.error(request, "Invalid request method. Please use the form to add products to your cart.")

    return redirect('product:products')

def my_card(request):

    cart = request.session.get('cart', {})
    cart_items = []


    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, product_id=product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })

    total_price = sum(item['total_price'] for item in cart_items)


    customer = getattr(request.user, 'customer', None)
    if customer:
        budget = customer.budget
    else:
        budget = None 

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'budget': budget,
    }

    return render(request, 'product/my_card.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Product removed from your cart.")
    else:
        messages.error(request, "Product not found in your cart.")

    return redirect('product:my_card') 


def confirm_cart(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to confirm your cart.")
        return redirect('customer:login')


    cart = request.session.get('cart', {})
    customer = request.user.customer  

    total_price = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, product_id=product_id)
        total_price += product.price * quantity

    if total_price > customer.budget:
        messages.error(request, "You do not have enough budget to confirm this cart.")
        return redirect('product:my_card') 


    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, product_id=product_id)
        total_price = product.price * quantity

        # Create an order
        Order.objects.create(
            customer=customer,
            product=product,
            quantity=quantity,
            total_price=total_price,
            order_status='PENDING',
        )


    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request, "Your order has been placed successfully!")
    return redirect('index') 


def add_product(request):
    if request.method == 'POST':

        product_name = request.POST.get('product_name')
        stock = request.POST.get('stock')
        price = request.POST.get('price')


        if product_name and stock and price:
            Product.objects.create(
                product_name=product_name,
                stock=int(stock),
                price=float(price),
            )
            messages.success(request, "Product added successfully!")
            return redirect('administration:dashboard')  
        else:
            messages.error(request, "All fields are required!")

    return render(request, 'product/add_product.html')

def edit_product(request, product_id):

    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":

        product.product_name = request.POST.get('product_name')
        product.stock = request.POST.get('stock')
        product.price = request.POST.get('price')


        product.save()

        return redirect('administration:dashboard')


    context = {'product': product}

    return render(request, "product/edit_product.html", context)


def decline_order(request, order_id):

    order = get_object_or_404(Order, order_id=order_id)


    if order.order_status != 'CANCELLED':
        order.order_status = 'CANCELLED'
        order.save()
        messages.success(request, f"Order {order_id} has been declined.")
    else:
        messages.warning(request, f"Order {order_id} is already declined.")

    return redirect('administration:dashboard')


def my_orders(request):
    
    if hasattr(request.user, 'customer'):
        orders = Order.objects.filter(customer=request.user.customer).order_by('-order_date')
    else:
        orders = []

    return render(request, 'product/my_orders.html', {'orders': orders})