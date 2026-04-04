from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def dossier_list(request):
    return render(request, 'dossiers/list.html')


@login_required
def dossier_detail(request, pk):
    return render(request, 'dossiers/detail.html')


@login_required
def dossier_create(request):
    return render(request, 'dossiers/form.html')


@login_required
def dossier_update(request, pk):
    return render(request, 'dossiers/form.html')