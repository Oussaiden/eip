from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from datetime import timedelta
from decimal import Decimal
from .models import Devis, VarianteDevis, LigneDevis, Dossier, LigneDossier
from .forms import DevisForm, VarianteDevisForm, LigneDevisForm, DossierForm
from apps.articles.models import ArticleStock, ArticleService
from apps.parametres.models import Parametre, Section


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
    from django.db.models import Count
    devis = Devis.objects.filter(is_deleted=False).select_related('client').annotate(
        nb_variantes=Count('variantes', filter=Q(variantes__is_deleted=False))
    )
    if search:
        from decimal import Decimal, InvalidOperation
        q = Q(numero__icontains=search) | Q(client__raison_sociale__icontains=search)
        try:
            montant = Decimal(search.replace('\u202f', '').replace(' ', '').replace(',', '.'))
            q |= Q(ttc=montant)
        except InvalidOperation:
            pass
        devis = devis.filter(q)
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

    variante_acceptee = variantes.filter(statut='accepte').first()
    nb_variantes = variantes.count()

    if variante_acceptee:
        total_context = {'mode': 'acceptee', 'variante': variante_acceptee}
    elif nb_variantes == 1:
        total_context = {'mode': 'unique', 'variante': variantes.first()}
    elif nb_variantes > 1:
        ttc_values = [v.ttc for v in variantes]
        ht_values = [v.ht for v in variantes]
        gain_values = [v.gain for v in variantes]
        total_context = {
            'mode': 'fourchette',
            'nb': nb_variantes,
            'ttc_min': min(ttc_values),
            'ttc_max': max(ttc_values),
            'ht_min': min(ht_values),
            'ht_max': max(ht_values),
            'gain_min': min(gain_values),
            'gain_max': max(gain_values),
        }
    else:
        total_context = {'mode': 'vide'}

    # Données par section pour chaque variante
    sections_actives = Section.objects.filter(actif=True).order_by('ordre', 'libelle')
    variantes_data = []
    for variante in variantes:
        sections_data = []
        for section in sections_actives:
            lignes = list(variante.lignes.filter(section=section).order_by('ordre'))
            if not lignes:
                continue
            lignes_chiffrees = [l for l in lignes if l.type in ('article', 'libre')]
            ht = sum((l.ht for l in lignes_chiffrees), Decimal('0'))
            tgc = sum((l.tgc for l in lignes_chiffrees), Decimal('0'))
            ttc = ht + tgc
            gain = sum((l.gain for l in lignes_chiffrees), Decimal('0'))
            sections_data.append({
                'section': section,
                'label': section.libelle,
                'lignes': lignes,
                'ht': ht,
                'tgc': tgc,
                'ttc': ttc,
                'gain': gain,
            })
        # Lignes sans section
        lignes_sans_section = list(variante.lignes.filter(section__isnull=True).order_by('ordre'))
        if lignes_sans_section:
            lignes_chiffrees = [l for l in lignes_sans_section if l.type in ('article', 'libre')]
            ht = sum((l.ht for l in lignes_chiffrees), Decimal('0'))
            tgc = sum((l.tgc for l in lignes_chiffrees), Decimal('0'))
            sections_data.append({
                'section': None,
                'label': 'Sans section',
                'lignes': lignes_sans_section,
                'ht': ht,
                'tgc': tgc,
                'ttc': ht + tgc,
                'gain': sum((l.gain for l in lignes_chiffrees), Decimal('0')),
            })
        variantes_data.append({
            'variante': variante,
            'sections': sections_data,
        })

    return render(request, 'dossiers/devis_detail.html', {
        'devis': devis,
        'variantes': variantes,
        'variantes_data': variantes_data,
        'peut_voir_gain': peut_voir_gain,
        'total_context': total_context,
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
def devis_dupliquer(request, pk):
    devis = get_object_or_404(Devis, pk=pk, is_deleted=False)
    if request.method == 'POST':
        nouveau = Devis.objects.create(
            client=devis.client,
            date=timezone.now().date(),
            date_validite=devis.date_validite,
            description=devis.description,
            notes=devis.notes,
            remise_globale=devis.remise_globale,
            created_by=request.user,
        )
        for variante in devis.variantes.filter(is_deleted=False):
            nouvelle_variante = VarianteDevis.objects.create(
                devis=nouveau,
                libelle=variante.libelle,
                remise_globale=variante.remise_globale,
                ordre=variante.ordre,
            )
            for ligne in variante.lignes.all():
                LigneDevis.objects.create(
                    variante=nouvelle_variante,
                    type=ligne.type,
                    section=ligne.section,
                    article=ligne.article,
                    article_service=ligne.article_service,
                    designation=ligne.designation,
                    qte=ligne.qte,
                    pu=ligne.pu,
                    pru=ligne.pru,
                    taux_tgc=ligne.taux_tgc,
                    remise=ligne.remise,
                    ordre=ligne.ordre,
                )
            nouvelle_variante.recalculer()
        messages.success(request, f'Devis {nouveau.numero} créé par duplication de {devis.numero}.')
        return redirect('dossiers:detail', pk=nouveau.pk)
    return redirect('dossiers:detail', pk=devis.pk)


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
def variante_dupliquer(request, pk):
    variante = get_object_or_404(VarianteDevis, pk=pk, is_deleted=False)
    devis = variante.devis
    if request.method == 'POST':
        nouvelle = VarianteDevis.objects.create(
            devis=devis,
            libelle=f"{variante.libelle} (copie)",
            remise_globale=variante.remise_globale,
            ordre=devis.variantes.count(),
        )
        for ligne in variante.lignes.all():
            LigneDevis.objects.create(
                variante=nouvelle,
                type=ligne.type,
                section=ligne.section,
                article=ligne.article,
                article_service=ligne.article_service,
                designation=ligne.designation,
                qte=ligne.qte,
                pu=ligne.pu,
                pru=ligne.pru,
                taux_tgc=ligne.taux_tgc,
                remise=ligne.remise,
                ordre=ligne.ordre,
            )
        nouvelle.recalculer()
        messages.success(request, f'Variante « {nouvelle.libelle} » créée.')
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
            elif ligne.article_service and not ligne.designation:
                ligne.designation = ligne.article_service.designation
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
            elif l.article_service and not l.designation:
                l.designation = l.article_service.designation
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
def article_stock_info(request, pk):
    article = get_object_or_404(ArticleStock, pk=pk, actif=True)
    return JsonResponse({
        'designation': article.designation,
        'pu': str(article.prix_vente_ht),
        'pru': str(article.pru_moyen),
        'taux_tgc': str(article.tgc_vente.taux) if article.tgc_vente else '0',
        'tgc_id': str(article.tgc_vente.id) if article.tgc_vente else '',
        'unite': article.unite.abreviation,
    })


@login_required
def article_service_info(request, pk):
    article = get_object_or_404(ArticleService, pk=pk, actif=True)
    return JsonResponse({
        'designation': article.designation,
        'pu': str(article.prix_vente_ht),
        'pru': '0',
        'taux_tgc': str(article.tgc_vente.taux) if article.tgc_vente else '0',
        'tgc_id': str(article.tgc_vente.id) if article.tgc_vente else '',
        'unite': article.unite.abreviation,
    })


@login_required
def articles_par_section(request, section_pk):
    stocks = ArticleStock.objects.filter(actif=True, sections=section_pk).order_by('designation')
    services = ArticleService.objects.filter(actif=True, sections=section_pk).order_by('designation')
    return JsonResponse({
        'stocks': [{'id': str(a.pk), 'text': f"{a.reference} — {a.designation}"} for a in stocks],
        'services': [{'id': str(a.pk), 'text': f"{a.reference} — {a.designation}"} for a in services],
    })


@login_required
def devis_pdf(request, pk):
    devis = get_object_or_404(Devis, pk=pk, is_deleted=False)
    variantes = devis.variantes.filter(is_deleted=False).prefetch_related('lignes')
    sections_actives = Section.objects.filter(actif=True).order_by('ordre', 'libelle')

    variantes_data = []
    for variante in variantes:
        sections_data = []
        for section in sections_actives:
            lignes = list(variante.lignes.filter(section=section).order_by('ordre'))
            if not lignes:
                continue
            lignes_chiffrees = [l for l in lignes if l.type in ('article', 'libre')]
            ht = sum((l.ht for l in lignes_chiffrees), Decimal('0'))
            tgc = sum((l.tgc for l in lignes_chiffrees), Decimal('0'))
            sections_data.append({
                'label': section.libelle,
                'lignes': lignes,
                'ht': ht,
                'tgc': tgc,
                'ttc': ht + tgc,
            })
        lignes_sans_section = list(variante.lignes.filter(section__isnull=True).order_by('ordre'))
        if lignes_sans_section:
            lignes_chiffrees = [l for l in lignes_sans_section if l.type in ('article', 'libre')]
            ht = sum((l.ht for l in lignes_chiffrees), Decimal('0'))
            tgc = sum((l.tgc for l in lignes_chiffrees), Decimal('0'))
            sections_data.append({
                'label': 'Divers',
                'lignes': lignes_sans_section,
                'ht': ht,
                'tgc': tgc,
                'ttc': ht + tgc,
            })
        variantes_data.append({'variante': variante, 'sections': sections_data})

    def get_param(cle, defaut=''):
        try:
            return Parametre.objects.get(cle=cle).valeur
        except Parametre.DoesNotExist:
            return defaut

    societe = {
        'nom': get_param('nom_societe', 'EIP Imprimerie'),
        'adresse': get_param('adresse_societe', ''),
        'telephone': get_param('telephone_societe', ''),
        'email': get_param('email_societe', ''),
        'siret': get_param('siret_societe', ''),
    }

    html_string = render_to_string('dossiers/devis_pdf.html', {
        'devis': devis,
        'variantes_data': variantes_data,
        'societe': societe,
        'request': request,
    })

    from weasyprint import HTML
    pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="devis_{devis.numero}.pdf"'
    return response


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