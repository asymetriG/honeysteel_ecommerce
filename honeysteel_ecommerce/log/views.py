from django.shortcuts import render
from django.core.paginator import Paginator
from log.models import Log 


# Create your views here.
def logs_page(request):
    logs = Log.objects.all().order_by('-log_date')  
    paginator = Paginator(logs, 10) 

    page_number = request.GET.get('page')  
    page_obj = paginator.get_page(page_number)  

    context = {
        'page_obj': page_obj,  
    }
    return render(request, 'log/logs.html', context)