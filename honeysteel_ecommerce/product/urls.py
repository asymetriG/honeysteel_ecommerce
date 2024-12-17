
from django.urls import path
from . import views

app_name = "product"

urlpatterns = [
    path("edit_product/<int:product_id>/",views.edit_product,name="edit_product")
]