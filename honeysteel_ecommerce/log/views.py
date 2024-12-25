from django.shortcuts import render
from django.core.paginator import Paginator
from log.models import Log  # Assuming the Log model is in the logs app


# Create your views here.
def logs_page(request):
    logs = Log.objects.all().order_by('-log_date')  # Fetch logs, newest first
    paginator = Paginator(logs, 10)  # Show 10 logs per page

    page_number = request.GET.get('page')  # Get the current page number
    page_obj = paginator.get_page(page_number)  # Get the logs for the current page

    context = {
        'page_obj': page_obj,  # Logs for the current page
    }
    return render(request, 'log/logs.html', context)