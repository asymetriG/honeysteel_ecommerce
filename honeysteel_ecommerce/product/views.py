from django.shortcuts import render,get_list_or_404,get_object_or_404,redirect
from .models import Product
from django.contrib import messages



def add_to_cart(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 0))

        if quantity > 0 and quantity <= product.stock:
            # Simulate adding to cart: You can replace this with real cart logic
            request.session['cart'] = request.session.get('cart', {})
            cart = request.session['cart']

            if product_id in cart:
                cart[product_id] += quantity
            else:
                cart[product_id] = quantity

            request.session.modified = True
            messages.success(request, f"{quantity} x '{product.product_name}' added to cart.")
        else:
            messages.error(request, "Invalid quantity. Please check stock availability.")

    return redirect('index')  

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