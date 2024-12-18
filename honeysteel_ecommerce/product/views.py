from django.shortcuts import render,get_list_or_404,get_object_or_404,redirect
from .models import Product,Order
from django.contrib import messages

# Create your views here.
def products(request):
    # Fetch all products
    products = Product.objects.all()

    # Pass products to the template
    context = {'products': products}
    return render(request, 'product/products.html', context)

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    product_id = str(product_id)  # Convert product_id to string to use as key in session

    if request.method == "POST":
        # Get the quantity from the form
        quantity = int(request.POST.get("quantity", 0))

        # Validate quantity
        if quantity <= 0 or quantity > product.stock or quantity > 5:
            messages.error(request, "Invalid quantity. Check stock availability. (Max: 5 items)")
            return redirect('product:products')

        # Retrieve or initialize the cart
        cart = request.session.get('cart', {})

        # Check if the product is already in the cart
        if product_id in cart:
            # If adding more exceeds the maximum limit, show an error
            if cart[product_id] + quantity > 5:
                messages.error(request, "Cannot add more than 5 of this product to the cart.")
                return redirect('product:products')

            # Update the quantity in the cart
            cart[product_id] += quantity
        else:
            # Add the product to the cart
            cart[product_id] = quantity

        # Save the updated cart to the session
        request.session['cart'] = cart
        request.session.modified = True

        messages.success(request, f"{quantity} x '{product.product_name}' added to cart.")
    else:
        messages.error(request, "Invalid request method. Please use the form to add products to your cart.")

    return redirect('product:products')

def my_card(request):
    # Retrieve cart from session
    cart = request.session.get('cart', {})
    cart_items = []

    # Build a list of cart items with product details
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, product_id=product_id)
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'total_price': product.price * quantity
        })

    # Calculate the total price of all items in the cart
    total_price = sum(item['total_price'] for item in cart_items)

    # Fetch user's budget
    customer = getattr(request.user, 'customer', None)
    if customer:
        budget = customer.budget
    else:
        budget = None  # Handle case where user is not a customer

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'budget': budget,
    }

    return render(request, 'product/my_card.html', context)

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]  # Remove the product from the cart
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "Product removed from your cart.")
    else:
        messages.error(request, "Product not found in your cart.")

    return redirect('product:my_card')  # Redirect back to the cart page


def confirm_cart(request):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to confirm your cart.")
        return redirect('customer:login')  # Redirect to login or home page

    # Retrieve the user's cart and customer profile
    cart = request.session.get('cart', {})
    customer = request.user.customer  # Assumes `Customer` is linked to `User`

    # Ensure the budget is sufficient
    total_price = 0
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, product_id=product_id)
        total_price += product.price * quantity

    if total_price > customer.budget:
        messages.error(request, "You do not have enough budget to confirm this cart.")
        return redirect('product:my_card')  # Redirect back to the cart

    # Generate orders for each cart item
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

        # Update product stock
        # product.stock -= quantity
        # product.save()

    # Deduct the total price from the customer's budget
    # customer.budget -= total_price
    # customer.save()

    # Clear the cart
    request.session['cart'] = {}
    request.session.modified = True

    messages.success(request, "Your order has been placed successfully!")
    return redirect('index')  # Redirect to a confirmation or home page


def add_product(request):
    if request.method == 'POST':
        # Get form data
        product_name = request.POST.get('product_name')
        stock = request.POST.get('stock')
        price = request.POST.get('price')

        # Validate and save the product
        if product_name and stock and price:
            Product.objects.create(
                product_name=product_name,
                stock=int(stock),
                price=float(price),
            )
            messages.success(request, "Product added successfully!")
            return redirect('administration:dashboard')  # Redirect back to the dashboard
        else:
            messages.error(request, "All fields are required!")

    return render(request, 'product/add_product.html')

def edit_product(request, product_id):
    # Fetch the product to be edited or return 404
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        # Update product fields with POST data
        product.product_name = request.POST.get('product_name')
        product.stock = request.POST.get('stock')
        product.price = request.POST.get('price')

        # Save updated product
        product.save()

        # Redirect to dashboard after successful edit
        return redirect('administration:dashboard')

    # Render the edit form with product details
    context = {'product': product}

    return render(request, "product/edit_product.html", context)


def decline_order(request, order_id):
    # Retrieve the order or return a 404 error
    order = get_object_or_404(Order, order_id=order_id)

    # Update the order status to CANCELLED
    if order.order_status != 'CANCELLED':
        order.order_status = 'CANCELLED'
        order.save()
        messages.success(request, f"Order {order_id} has been declined.")
    else:
        messages.warning(request, f"Order {order_id} is already declined.")

    return redirect('administration:dashboard')  # Redirect back to the dashboard