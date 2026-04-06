from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Devis, VarianteDevis, LigneDevis, Dossier, LigneDossier
from .forms import DevisForm, VarianteDevisForm, LigneDevisForm, DossierForm
from apps.articles.models import Article
from apps.parametres.models import Parametre


def get_delai_validite():
    try:
        p = Parametre.objects.get(cle='delai_validite_devis')
        return int(p.valeur)
    except Exception:
        return 30


@login_required
def devis_list(request):
    search = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    devis = Devis.objects.filter(is_deleted=False).select_related('client')
    if search:
        devis = devis.filter(
            Q(numero__icontains=search) |
            Q(client__raison_sociale__icontains=search)
        )
    if statut:
        devis = devis.filter(statut=statut)
    return render(request, 'dossiers/devis_list.html', {
        'devis_list': devis,
        'search': search,
        'statut': statut,
        'statuts': Devis.STATUTS,
    })


@login_required
def devis_detail(request, pk):
    devis = get_object_or_404(Devis, pk=pk, is_deleted=False)
    variantes = devis.variantes.filter(is_deleted=False).prefetch_related('lignes')
    peut_voir_gain = request.user.role in ['direction', 'technico_commercial'] or request.user.is_staff
    return render(request, 'dossiers/devis_detail.html', {
        'devis': devis,
        'variantes': variantes,
        'peut_voir_gain': peut_voir_gain,
    })


@login_required
def devis_create(request):
    delai = get_delai_validite()
    if request.method == 'POST':
        form = DevisForm(request.POST)
        if form.is_valid():
            devis = form.save(commit=False)
            devis.created_by = request.user
            if not devis.date_validite:
                devis.date_validite = devis.date + timedelta(days=delai)
            devis.save()
            messages.success(request, f'Devis {devis.numero} créé avec succès.')
            return redirect('dossiers:detail', pk=devis.pk)
    else:
        today = timezone.now().date()
        form = DevisForm(initial={
            'date': today,
            'date_validite': today + timedelta(days=delai),
        })
    return render(request, 'dossiers/devis_form.html', {
        'form': form,
        'titre': 'Nouveau devis',
        'delai_validite': delai,
    })


@login_required
def devis_update(request, pk):
    devis = get_object_or_404(Devis, pk=pk, is_deleted=False)
    delai = get_delai_validite()
    if request.method == 'POST':
        form = DevisForm(request.POST, instance=devis)
        if form.is_valid():
            form.save()
            messages.success(request, f'Devis {devis.numero} modifié avec succès.')
            return redirect('dossiers:detail', pk=devis.pk)
    else:
        form = DevisForm(instance=devis)
    return render(request, 'dossiers/devis_form.html', {
        'form': form,
        'titre': f'Modifier {devis.numero}',
        'devis': devis,
        'delai_validite': delai,
    })


@login_required
def devis_delete(request, pk):
    devis = get_object_or_404(Devis, pk=pk, is_deleted=False)
    if request.method == 'POST':
        devis.is_deleted = True
        devis.save()
        messages.success(request, f'Devis {devis.numero} supprimé.')
        return redirect('dossiers:list')
    return render(request, 'dossiers/devis_confirm_delete.html', {'devis': devis})


@login_required
def variante_create(request, devis_pk):
    devis = get_object_or_404(Devis, pk=devis_pk, is_deleted=False)
    if request.method == 'POST':
        form = VarianteDevisForm(request.POST)
        if form.is_valid():
            variante = form.save(commit=False)
            variante.devis = devis
            variante.ordre = devis.variantes.count()
            variante.save()
            messages.success(request, f'Variante {variante.libelle} créée.')
            return redirect('dossiers:detail', pk=devis.pk)
    else:
        form = VarianteDevisForm()
    return render(request, 'dossiers/variante_form.html', {
        'form': form,
        'devis': devis,
        'titre': 'Nouvelle variante',
    })


@login_required
def variante_update(request, pk):
    variante = get_object_or_404(VarianteDevis, pk=pk, is_deleted=False)
    devis = variante.devis
    if request.method == 'POST':
        form = VarianteDevisForm(request.POST, instance=variante)
        if form.is_valid():
            form.save()
            messages.success(request, f'Variante {variante.libelle} modifiée.')
            return redirect('dossiers:detail', pk=devis.pk)
    else:
        form = VarianteDevisForm(instance=variante)
    return render(request, 'dossiers/variante_form.html', {
        'form': form,
        'devis': devis,
        'titre': f'Modifier variante {variante.libelle}',
    })


@login_required
def variante_delete(request, pk):
    variante = get_object_or_404(VarianteDevis, pk=pk, is_deleted=False)
    devis = variante.devis
    if request.method == 'POST':
        variante.is_deleted = True
        variante.save()
        messages.success(request, f'Variante {variante.libelle} supprimée.')
    return redirect('dossiers:detail', pk=devis.pk)


@login_required
def variante_accepter(request, pk):
    variante = get_object_or_404(VarianteDevis, pk=pk, is_deleted=False)
    devis = variante.devis
    if request.method == 'POST':
        variante.statut = 'accepte'
        variante.save()
        devis.variantes.exclude(pk=pk).update(statut='refuse')
        devis.statut = 'accepte'
        devis.sent_at = timezone.now()
        devis.save()
        dossier = Dossier.objects.create(
            variante=variante,
            client=devis.client,
            created_by=request.user,
        )
        messages.success(request, f'Variante acceptée — Dossier {dossier.numero} créé.')
        return redirect('dossiers:dossier_detail', pk=dossier.pk)
    return render(request, 'dossiers/variante_accepter.html', {
        'variante': variante,
        'devis': devis,
    })


@login_required
def ligne_create(request, variante_pk):
    variante = get_object_or_404(VarianteDevis, pk=variante_pk, is_deleted=False)
    devis = variante.devis
    if request.method == 'POST':
        form = LigneDevisForm(request.POST)
        if form.is_valid():
            ligne = form.save(commit=False)
            ligne.variante = variante
            ligne.ordre = variante.lignes.count()
            if ligne.article and not ligne.designation:
                ligne.designation = ligne.article.designation
            ligne.save()
            messages.success(request, 'Ligne ajoutée.')
            return redirect('dossiers:detail', pk=devis.pk)
    else:
        form = LigneDevisForm()
    return render(request, 'dossiers/ligne_form.html', {
        'form': form,
        'variante': variante,
        'devis': devis,
        'titre': 'Nouvelle ligne',
    })


@login_required
def ligne_update(request, pk):
    ligne = get_object_or_404(LigneDevis, pk=pk)
    variante = ligne.variante
    devis = variante.devis
    if request.method == 'POST':
        form = LigneDevisForm(request.POST, instance=ligne)
        if form.is_valid():
            l = form.save(commit=False)
            if l.article and not l.designation:
                l.designation = l.article.designation
            l.save()
            messages.success(request, 'Ligne modifiée.')
            return redirect('dossiers:detail', pk=devis.pk)
    else:
        form = LigneDevisForm(instance=ligne)
    return render(request, 'dossiers/ligne_form.html', {
        'form': form,
        'variante': variante,
        'devis': devis,
        'titre': 'Modifier ligne',
    })


@login_required
def ligne_delete(request, pk):
    ligne = get_object_or_404(LigneDevis, pk=pk)
    variante = ligne.variante
    devis = variante.devis
    if request.method == 'POST':
        ligne.delete()
        variante.recalculer()
        messages.success(request, 'Ligne supprimée.')
    return redirect('dossiers:detail', pk=devis.pk)


@login_required
def article_info(request, pk):
    article = get_object_or_404(Article, pk=pk, actif=True)
    return JsonResponse({
        'designation': article.designation,
        'pu': str(article.prix_vente_ht),
        'pru': str(article.pru_moyen),
        'taux_tgc': str(article.tgc_vente.taux) if article.tgc_vente else '0',
        'tgc_id': str(article.tgc_vente.id) if article.tgc_vente else '',
        'unite': article.unite.abreviation,
    })


@login_required
def dossier_list(request):
    search = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    dossiers = Dossier.objects.filter(is_deleted=False).select_related('client')
    if search:
        dossiers = dossiers.filter(
            Q(numero__icontains=search) |
            Q(client__raison_sociale__icontains=search)
        )
    if statut:
        dossiers = dossiers.filter(statut=statut)
    return render(request, 'dossiers/dossier_list.html', {
        'dossiers': dossiers,
        'search': search,
        'statut': statut,
        'statuts': Dossier.STATUTS,
    })


@login_required
def dossier_detail(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk, is_deleted=False)
    peut_voir_gain = request.user.role in ['direction', 'technico_commercial'] or request.user.is_staff
    pointages = dossier.pointages.all().order_by('-created_at')
    return render(request, 'dossiers/dossier_detail.html', {
        'dossier': dossier,
        'peut_voir_gain': peut_voir_gain,
        'pointages': pointages,
    })