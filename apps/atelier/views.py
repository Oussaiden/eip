from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from apps.dossiers.models import Dossier, LigneDossier, PointageAtelier
from apps.accounts.models import User


def scan_badge(request):
    erreur = None

    if request.method == 'POST':
        badge = request.POST.get('badge', '').strip()
        try:
            User.objects.get(username=badge)
            url = reverse('atelier:scan_dossier') + f'?badge={badge}'
            return redirect(url)
        except User.DoesNotExist:
            erreur = f"Badge inconnu : {badge}"

    return render(request, 'atelier/scan_badge.html', {'erreur': erreur})


def scan_dossier(request):
    badge = request.GET.get('badge', '') or request.POST.get('badge', '')
    erreur = None

    try:
        operateur = User.objects.get(username=badge)
    except User.DoesNotExist:
        return redirect('atelier:scan_badge')

    dossiers_assignes = Dossier.objects.filter(
        statut='en_fabrication',
        creneaux__operateur=operateur
    ).distinct().order_by('-priorite', 'date_livraison')

    if request.method == 'POST':
        numero_dossier = request.POST.get('numero_dossier', '').strip()
        try:
            dossier = Dossier.objects.get(numero=numero_dossier)
            url = reverse('atelier:taches', args=[dossier.numero]) + f'?badge={badge}'
            return redirect(url)
        except Dossier.DoesNotExist:
            erreur = f"Dossier inconnu : {numero_dossier}"

    return render(request, 'atelier/scan_dossier.html', {
        'operateur': operateur,
        'badge': badge,
        'dossiers_assignes': dossiers_assignes,
        'erreur': erreur,
    })


def taches(request, numero):
    dossier = get_object_or_404(Dossier, numero=numero)
    badge = request.GET.get('badge', '') or request.POST.get('badge', '')

    try:
        operateur = User.objects.get(username=badge)
    except User.DoesNotExist:
        return redirect('atelier:scan_badge')

    lignes = dossier.lignes.select_related('type', 'article').all()

    if request.method == 'POST':
        ligne_id = request.POST.get('ligne_id')
        ligne = get_object_or_404(LigneDossier, pk=ligne_id, dossier=dossier)

        pointage = PointageAtelier.objects.create(
            dossier=dossier,
            operateur=operateur,
            ligne_dossier=ligne,
            type_tache=ligne.type,
            qte_prevue=ligne.qte_prevue,
            statut='en_cours',
        )
        return redirect('atelier:valider', pk=pointage.pk)

    return render(request, 'atelier/taches.html', {
        'dossier': dossier,
        'operateur': operateur,
        'lignes': lignes,
        'badge': badge,
    })


def valider(request, pk):
    pointage = get_object_or_404(PointageAtelier, pk=pk)

    if request.method == 'POST':
        qte_reelle = request.POST.get('qte_reelle', '0')
        notes = request.POST.get('notes', '')
        try:
            qte_reelle = float(qte_reelle.replace(',', '.'))
        except ValueError:
            qte_reelle = 0
        pointage.terminer(qte_reelle=qte_reelle, notes=notes)
        messages.success(request, f'Pointage enregistré — {pointage.type_tache.libelle}')
        return redirect('atelier:scan_badge')

    return render(request, 'atelier/valider.html', {
        'pointage': pointage,
    })