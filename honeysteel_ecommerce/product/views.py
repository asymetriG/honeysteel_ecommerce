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

    return redirect('index')  # Redirect back to the products page

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