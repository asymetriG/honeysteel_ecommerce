
from django.urls import path
from . import views

app_name = "product"

urlpatterns = [
    path("edit_product/<int:product_id>/",views.edit_product,name="edit_product"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('my-card/', views.my_card, name='my_card'),  
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('products',views.products,name="products"),
    path('add-product/', views.add_product, name='add_product'), 
    path('confirm_cart',views.confirm_cart,name="confirm_cart"),
    path('decline-order/<int:order_id>/', views.decline_order, name='decline_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('confirm-all-orders/', views.confirm_all_orders, name='confirm_all_orders'),
    path('reset-db/', views.reset_db, name='reset_db'),
]