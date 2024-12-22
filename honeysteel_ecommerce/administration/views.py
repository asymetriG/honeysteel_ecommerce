from django.shortcuts import render,redirect
from product.models import Customer,Product,Order
import random
from django.contrib.auth.models import User
from django.http import JsonResponse


# Create your views here.
def index(request):
    return render(request, 'index.html')


def dashboard(request):
    customers = Customer.objects.all()  # Fetch all customers from the database
    products = Product.objects.all()
    orders = Order.objects.all()
    
    product_names = [product.product_name for product in products]
    product_stocks = [product.stock for product in products]
    low_stock_products = [product for product in products if product.stock < 10]


    context = {
        'customers': customers,
        'products': products,
        'orders': orders,
        'product_names': product_names,
        'product_stocks': product_stocks,
        'low_stock_products': low_stock_products,  

    }

    return render(request, 'administration/dashboard.html', context)



def generate_customers(request):
    if request.method == "POST":
        # Clear existing customers (optional)
        # Customer.objects.all().delete()

        # List of sample names
        names = ["Alice", "Bob", "Charlie", "Diana", "Ethan", "Fiona", "George", "Hannah"]

        # Generate 5-10 customers
        for i in range(random.randint(5, 10)):
            name = random.choice(names)
            names.remove(name)  # Ensure unique names

            # Randomize user creation (this assumes username uniqueness)
            user = User.objects.create_user(username=f"user_{i}_{random.randint(100, 999)}", password="password123")

            # Assign budget and customer type
            budget = round(random.uniform(500, 3000), 2)
            customer_type = "Premium" if i < 2 else "Normal"  # Ensure at least 2 "Premium" customers

            # Create customer instance
            Customer.objects.create(
                user=user,
                customer_name=name,
                budget=budget,
                customer_type=customer_type,
                total_spent=0.0
            )

        return JsonResponse({"success": True, "message": "Random customers generated successfully!"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method!"})