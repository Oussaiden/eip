from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def article_list(request):
    return render(request, 'articles/list.html')


@login_required
def article_detail(request, pk):
    return render(request, 'articles/detail.html')


@login_required
def article_create(request):
    return render(request, 'articles/form.html')


@login_required
def article_update(request, pk):
    return render(request, 'articles/form.html')
