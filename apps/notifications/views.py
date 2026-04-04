from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def notification_list(request):
    return render(request, 'notifications/list.html')