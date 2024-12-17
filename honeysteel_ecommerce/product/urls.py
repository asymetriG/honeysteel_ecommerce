
from django.urls import path
from . import views

app_name = "product"

urlpatterns = [
    path("edit_product/<int:product_id>/",views.edit_product,name="edit_product"),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('my-card/', views.my_card, name='my_card'),  
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),


]