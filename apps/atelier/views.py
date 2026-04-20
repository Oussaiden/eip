from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from apps.dossiers.models import Dossier, LigneDossier, PointageAtelier
from apps.accounts.models import User
from apps.planning.models import Machine
from .forms import MachineForm


# ── Machine ───────────────────────────────────────────────────────────────────

@login_required
def machine_list(request):
    machines = Machine.objects.select_related('type').filter(actif=True)
    return render(request, 'atelier/machine_list.html', {'machines': machines})


@login_required
def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    simulations = []
    for n in [100, 500, 1000, 2000, 5000, 10000]:
        simulations.append({
            'qte': n,
            'cout_total': machine.calculer_cout_total(n),
            'pu': machine.calculer_pu(n),
        })
    return render(request, 'atelier/machine_detail.html', {
        'machine': machine,
        'simulations': simulations,
    })


@login_required
def machine_create(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save()
            messages.success(request, f'Machine {machine.nom} créée.')
            return redirect('atelier:machine_detail', pk=machine.pk)
    else:
        form = MachineForm()
    return render(request, 'atelier/machine_form.html', {
        'form': form,
        'titre': 'Nouvelle machine',
    })


@login_required
def machine_update(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, f'Machine {machine.nom} modifiée.')
            return redirect('atelier:machine_detail', pk=machine.pk)
    else:
        form = MachineForm(instance=machine)
    return render(request, 'atelier/machine_form.html', {
        'form': form,
        'titre': f'Modifier {machine.nom}',
        'machine': machine,
    })


# ── Atelier scan ──────────────────────────────────────────────────────────────

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
    return render(request, 'atelier/valider.html', {'pointage': pointage})
