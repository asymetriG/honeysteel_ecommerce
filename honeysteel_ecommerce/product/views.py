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
from log.models import Log  # Assuming Log model is in logs app

product_locks = defaultdict(threading.Lock)
processing_start_times = {}


def calculate_priority(order):
    base_priority = 15 if order.customer.customer_type == "Premium" else 10
    wait_time = (now() - order.order_date).total_seconds()
    wait_time_weight = 0.5
    return base_priority + (wait_time * wait_time_weight)



def process_order(order,queue_start_time):

    global product_locks,processing_start_times


    product_lock = product_locks[order.product.product_id]

    with product_lock:  
        with transaction.atomic():  
            
            current_time = time.time()
            
            if current_time - queue_start_time > 15:
            
                order.order_status = "CANCELLED"
                order.save()

              
                Log.save_log(
                    log_type="ERROR",
                    log_details=f"Order {order.id} canceled due to timeout after 15 seconds.",
                    customer=order.customer,
                    order=order,
                )
                return
            
            product = Product.objects.select_for_update().get(product_id=order.product.product_id)

           
            customer = order.customer.__class__.objects.select_for_update().get(pk=order.customer.pk)

            if order.quantity > product.stock:
                
                order.order_status = "CANCELLED"
                order.save()
                
                Log.save_log(
                    log_type="ERROR",
                    log_details=f"Order {order.id} canceled due to lack of stock",
                    customer=order.customer,
                    order=order,
                )
                return

           
            product.stock -= order.quantity
            product.save()

       
            customer.budget -= order.total_price

    
            customer.total_spent += order.total_price

            
            if customer.total_spent > 2000:
                customer.customer_type = "Premium"
                
                Log.save_log(
                    log_type="INFO",
                    log_details=f"Customer {order.customer} became a premium customer",
                    customer=order.customer,
                    order=order,
                )

           
            customer.save()

            
            order.order_status = "COMPLETED"
            order.save()
            
            Log.save_log(
                    log_type="INFO",
                    log_details=f"Order {order.order_id} processed",
                    customer=order.customer,
                    order=order,
            )
            
            processing_start_times[order.order_id] = time.time()
        
        
def reset_db(request):
 
    Order.objects.all().delete()

    Product.objects.all().delete()

    Log.objects.all().delete()

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
    
    Log.save_log(
        log_type="INFO",
        log_details="Database reset by admin.",
    )
    return redirect("administration:dashboard")  
        
def confirm_all_orders(request):
    if request.method == "GET":
        pending_orders = Order.objects.filter(order_status="PENDING")

        
        sorted_orders = sorted(pending_orders, key=calculate_priority, reverse=True)

        threads = []
        processing_start_times.clear()  

        for order in sorted_orders:
            
            queue_start_time = time.time()
            processing_start_times[order.order_id] = queue_start_time

            thread = threading.Thread(target=process_order, args=(order, queue_start_time))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        messages.success(request, "All pending orders have been processed.")
        Log.save_log(
            log_type="INFO",
            log_details=f"All pending orders have been processed.",
        )
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
            Log.save_log(
                log_type="ERROR",
                log_details=f"Customer {request.user.customer} could not add {product.product_name} to cart due to stock availability",
                customer=request.user.customer,
            )
            
            return redirect('product:products')


        cart = request.session.get('cart', {})


        if product_id in cart:

            if cart[product_id] + quantity > 5:
                messages.error(request, "Cannot add more than 5 of this product to the cart.")
                Log.save_log(
                    log_type="ERROR",
                    log_details=f"Customer {request.user.customer} could not add {product.product_name} to cart due to stock availability",
                    customer=request.user.customer,
                )
                return redirect('product:products')


            cart[product_id] += quantity
        else:

            cart[product_id] = quantity


        request.session['cart'] = cart
        request.session.modified = True

        messages.success(request, f"{quantity} x '{product.product_name}' added to cart.")
        Log.save_log(
            log_type="INFO",
            log_details=f"Customer {request.user.customer} added {product.product_name} to cart.",
            customer=request.user.customer,
        )
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
        Log.save_log(
            log_type="INFO",
            log_details=f"Customer {request.user.customer} removed product with id {product_id} from cart.",
            customer=request.user.customer,
        )
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
        
        Log.save_log(
            log_type="INFO",
            log_details=f"Customer {request.user.customer} could not confirm cart due to lack of budget",
            customer=request.user.customer,
        )
        messages.error(request, "You do not have enough budget to confirm this cart.")
        
        return redirect('product:my_card') 


    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, product_id=product_id)
        total_price = product.price * quantity

        # Create an order
        order = Order.objects.create(
            customer=customer,
            product=product,
            quantity=quantity,
            total_price=total_price,
            order_status='PENDING',
        )
        Log.save_log(
            log_type="INFO",
            log_details=f"Customer {request.user.customer} generated order {order}",
            customer=request.user.customer,
            order=order
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
            
            Log.save_log(
                log_type="INFO",
                log_details=f"Admin added product {product_name} with {stock} quantity",
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
        
        Log.save_log(
            log_type="INFO",
            log_details=f"Admin edited product {product.product_name} with {product.stock} quantity",
        )   

        return redirect('administration:dashboard')


    context = {'product': product}

    return render(request, "product/edit_product.html", context)




def decline_order(request, order_id):

    order = get_object_or_404(Order, order_id=order_id)


    if order.order_status == 'PENDING':
        order.order_status = 'CANCELLED'
        order.save()
        
        Log.save_log(
            log_type="INFO",
            log_details=f"Order {order.order_id} has been declined",
            order=order
        )   
        messages.success(request, f"Order {order_id} has been declined.")
        
    elif order.order_status=="COMPLETED":
        Log.save_log(
            log_type="ERROR",
            log_details=f"Order {order.order_id} could not have been declined because its condition is completed.",
            order=order
        ) 
        messages.error(request, f"Order {order_id} has been completed so it will not be declined.")
    else:
        messages.errorasd(request, f"Order {order_id} is already declined.")

    return redirect('administration:dashboard')


def my_orders(request):
    
    if hasattr(request.user, 'customer'):
        orders = Order.objects.filter(customer=request.user.customer).order_by('-order_date')
    else:
        orders = []

    return render(request, 'product/my_orders.html', {'orders': orders})