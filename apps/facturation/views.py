from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def facture_list(request):
    return render(request, 'facturation/list.html')


@login_required
def facture_detail(request, pk):
    return render(request, 'facturation/detail.html')
