from django.shortcuts import render,get_list_or_404,get_object_or_404,redirect
from .models import Product


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