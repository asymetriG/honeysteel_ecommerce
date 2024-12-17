from django.contrib import admindocs
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "administration"

urlpatterns = [
    path("dashboard/",views.dashboard,name="dashboard"),
    path('generate-customers/', views.generate_customers, name='generate_customers'),

]