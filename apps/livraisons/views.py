from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def livraison_list(request):
    return render(request, 'livraisons/list.html')


@login_required
def livraison_detail(request, pk):
    return render(request, 'livraisons/detail.html')
