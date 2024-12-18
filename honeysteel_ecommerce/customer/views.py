from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from customer.models import Customer


def login_view(request):
    
    if request.method == 'POST':
        
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            return redirect('index') 
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'customer/login.html')

def register_view(request):
    if request.method == 'POST':
        
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        
        if password1 == password2:
            try:
                User.objects.create_user(username=username, email=email, password=password1,first_name=first_name,last_name=last_name)
                
                messages.success(request, 'Account created successfully!')
                
                return redirect('customer:login')
            except:
                messages.error(request, 'Username already exists.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'customer/register.html')



def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('customer:login')  



def edit_customer(request, customer_id):
    customer = get_object_or_404(Customer, customer_id=customer_id)

    if request.method == "POST":
        # Get updated details from the form
        customer_name = request.POST.get("customer_name")
        budget = request.POST.get("budget")
        customer_type = request.POST.get("customer_type")

        # Update customer details
        if customer_name:
            customer.user.username = customer_name
            customer.user.save()  # Save the User model changes
        if budget:
            customer.budget = float(budget)
        if customer_type:
            customer.customer_type = customer_type

        customer.save()  # Save the Customer model changes
        messages.success(request, f"Customer {customer.user.username} updated successfully!")
        return redirect('administration:dashboard')  # Redirect back to the dashboard

    return render(request, 'customer/edit_customer.html', {'customer': customer})