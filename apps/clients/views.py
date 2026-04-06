from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Client, Contact, AdresseLivraison
from .forms import ClientForm, ContactForm, AdresseLivraisonForm


def get_periode_filter(queryset, periode, date_debut, date_fin, date_field='created_at'):
    today = timezone.now().date()
    if periode == 'mois':
        queryset = queryset.filter(**{f'{date_field}__month': today.month, f'{date_field}__year': today.year})
    elif periode == 'trimestre':
        trimestre_debut = today.replace(month=((today.month - 1) // 3) * 3 + 1, day=1)
        queryset = queryset.filter(**{f'{date_field}__gte': trimestre_debut})
    elif periode == 'annee':
        queryset = queryset.filter(**{f'{date_field}__year': today.year})
    elif periode == 'annee_derniere':
        queryset = queryset.filter(**{f'{date_field}__year': today.year - 1})
    elif periode == 'personnalise' and date_debut and date_fin:
        queryset = queryset.filter(**{f'{date_field}__gte': date_debut, f'{date_field}__lte': date_fin})
    return queryset


@login_required
def client_list(request):
    search = request.GET.get('q', '')
    actif_filter = request.GET.get('actif', '')
    clients = Client.objects.all()
    if search:
        clients = clients.filter(
            Q(raison_sociale__icontains=search) |
            Q(email__icontains=search) |
            Q(siret__icontains=search)
        )
    if actif_filter == '1':
        clients = clients.filter(actif=True)
    elif actif_filter == '0':
        clients = clients.filter(actif=False)
    clients = clients.order_by('raison_sociale')
    return render(request, 'clients/list.html', {
        'clients': clients,
        'search': search,
        'actif_filter': actif_filter,
    })


@login_required
def client_detail(request, pk):
    client = get_object_or_404(Client, pk=pk)
    today = timezone.now().date()
    onglet = request.GET.get('onglet', 'fiche')
    statut = request.GET.get('statut', '')
    periode = request.GET.get('periode', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')

    from apps.facturation.models import Facture
    from apps.livraisons.models import BonLivraison

    # ── Devis ────────────────────────────────────────────────
    devis = client.devis.all()
    if statut and onglet == 'devis':
        devis = devis.filter(statut=statut)
    if onglet == 'devis':
        devis = get_periode_filter(devis, periode, date_debut, date_fin, date_field='date')
    devis = devis.order_by('-date')

    # ── Dossiers FAB ─────────────────────────────────────────
    dossiers_fab = client.dossiers.all()
    if statut and onglet == 'dossiers':
        dossiers_fab = dossiers_fab.filter(statut=statut)
    if onglet == 'dossiers':
        dossiers_fab = get_periode_filter(dossiers_fab, periode, date_debut, date_fin, date_field='date')
    dossiers_fab = dossiers_fab.order_by('-date')

    # ── Factures ─────────────────────────────────────────────
    factures = Facture.objects.filter(client=client)
    if statut and onglet == 'factures':
        factures = factures.filter(statut=statut)
    if onglet == 'factures':
        factures = get_periode_filter(factures, periode, date_debut, date_fin, date_field='date')
    factures = factures.order_by('-date')

    # ── Livraisons ───────────────────────────────────────────
    livraisons = BonLivraison.objects.filter(client=client)
    if statut and onglet == 'livraisons':
        livraisons = livraisons.filter(statut=statut)
    if onglet == 'livraisons':
        livraisons = get_periode_filter(livraisons, periode, date_debut, date_fin, date_field='date')
    livraisons = livraisons.order_by('-date')

    # ── Résumé financier ─────────────────────────────────────
    ca_total = Facture.objects.filter(
        client=client,
        statut__in=['emise', 'payee']
    ).aggregate(total=Sum('ttc'))['total'] or 0

    solde_du = Facture.objects.filter(
        client=client,
        statut='emise'
    ).aggregate(total=Sum('solde'))['total'] or 0

    dossiers_en_cours = client.dossiers.filter(
        statut__in=['en_fabrication']
    ).count()

    return render(request, 'clients/detail.html', {
        'client': client,
        'devis': devis,
        'dossiers_fab': dossiers_fab,
        'factures': factures,
        'livraisons': livraisons,
        'today': today,
        'ca_total': ca_total,
        'solde_du': solde_du,
        'dossiers_en_cours': dossiers_en_cours,
        'nb_devis': client.devis.count(),
        'nb_dossiers': client.dossiers.count(),
        'nb_factures': Facture.objects.filter(client=client).count(),
        'nb_livraisons': BonLivraison.objects.filter(client=client).count(),
    })


@login_required
def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client {client.raison_sociale} créé avec succès.')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ClientForm()
    return render(request, 'clients/form.html', {'form': form, 'titre': 'Nouveau client'})


@login_required
def client_update(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, f'Client {client.raison_sociale} modifié avec succès.')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/form.html', {
        'form': form,
        'titre': f'Modifier {client.raison_sociale}',
        'client': client,
    })


# ── Contacts ────────────────────────────────────────────────

@login_required
def contact_create(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.client = client
            contact.save()
            messages.success(request, 'Contact ajouté avec succès.')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ContactForm()
    return render(request, 'clients/contact_form.html', {
        'form': form,
        'client': client,
        'titre': 'Nouveau contact',
    })


@login_required
def contact_update(request, client_pk, pk):
    client = get_object_or_404(Client, pk=client_pk)
    contact = get_object_or_404(Contact, pk=pk, client=client)
    if request.method == 'POST':
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contact modifié avec succès.')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = ContactForm(instance=contact)
    return render(request, 'clients/contact_form.html', {
        'form': form,
        'client': client,
        'titre': f'Modifier {contact.prenom} {contact.nom}',
        'contact': contact,
    })


@login_required
def contact_delete(request, client_pk, pk):
    client = get_object_or_404(Client, pk=client_pk)
    contact = get_object_or_404(Contact, pk=pk, client=client)
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact supprimé.')
    return redirect('clients:detail', pk=client.pk)


# ── Adresses ────────────────────────────────────────────────

@login_required
def adresse_create(request, client_pk):
    client = get_object_or_404(Client, pk=client_pk)
    if request.method == 'POST':
        form = AdresseLivraisonForm(request.POST)
        if form.is_valid():
            adresse = form.save(commit=False)
            adresse.client = client
            adresse.save()
            messages.success(request, 'Adresse ajoutée avec succès.')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = AdresseLivraisonForm()
    return render(request, 'clients/adresse_form.html', {
        'form': form,
        'client': client,
        'titre': 'Nouvelle adresse de livraison',
    })


@login_required
def adresse_update(request, client_pk, pk):
    client = get_object_or_404(Client, pk=client_pk)
    adresse = get_object_or_404(AdresseLivraison, pk=pk, client=client)
    if request.method == 'POST':
        form = AdresseLivraisonForm(request.POST, instance=adresse)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adresse modifiée avec succès.')
            return redirect('clients:detail', pk=client.pk)
    else:
        form = AdresseLivraisonForm(instance=adresse)
    return render(request, 'clients/adresse_form.html', {
        'form': form,
        'client': client,
        'titre': f'Modifier {adresse.libelle}',
        'adresse': adresse,
    })


@login_required
def adresse_delete(request, client_pk, pk):
    client = get_object_or_404(Client, pk=client_pk)
    adresse = get_object_or_404(AdresseLivraison, pk=pk, client=client)
    if request.method == 'POST':
        adresse.delete()
        messages.success(request, 'Adresse supprimée.')
    return redirect('clients:detail', pk=client.pk)