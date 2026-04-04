from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def achat_list(request):
    return render(request, 'achats/list.html')


@login_required
def achat_detail(request, pk):
    return render(request, 'achats/detail.html')
