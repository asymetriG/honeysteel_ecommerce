
from django.urls import path
from . import views

app_name = "log"

urlpatterns = [
    path('logs/', views.logs_page, name='logs_page'),
]