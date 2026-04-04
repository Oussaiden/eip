from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Parametre


@login_required
def parametres_index(request):
    parametres = Parametre.objects.all().order_by('categorie', 'libelle')
    categories = Parametre.CATEGORIES
    return render(request, 'parametres/index.html', {
        'parametres': parametres,
        'categories': categories,
    })


@login_required
def parametre_update(request, pk):
    return render(request, 'parametres/update.html')
