import csv
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.utils import timezone
from .models import Article, Fournisseur, ArticleFournisseur, MouvementStock
from .forms import ArticleForm, FournisseurForm, ArticleFournisseurForm, MouvementStockForm
from apps.parametres.models import Categorie


def get_mouvements_filtres(article, type_mouvement, date_debut, date_fin, limite):
    mouvements = article.mouvements.all().order_by('-created_at')
    if type_mouvement:
        mouvements = mouvements.filter(type=type_mouvement)
    if date_debut:
        mouvements = mouvements.filter(created_at__date__gte=date_debut)
    if date_fin:
        mouvements = mouvements.filter(created_at__date__lte=date_fin)
    try:
        limite_int = int(limite)
    except (ValueError, TypeError):
        limite_int = 50
    return mouvements[:limite_int]


@login_required
def article_list(request):
    search = request.GET.get('q', '')
    categorie = request.GET.get('categorie', '')
    stock_bas = request.GET.get('stock_bas', '')

    articles = Article.objects.filter(actif=True)

    if search:
        articles = articles.filter(
            Q(reference__icontains=search) |
            Q(designation__icontains=search)
        )
    if categorie:
        articles = articles.filter(categorie__pk=categorie)
    if stock_bas == '1':
        articles = [a for a in articles if a.stock_bas]

    return render(request, 'articles/list.html', {
        'articles': articles,
        'search': search,
        'categorie': categorie,
        'stock_bas': stock_bas,
        'categories': Categorie.objects.filter(actif=True),
    })


@login_required
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    type_mouvement = request.GET.get('type_mouvement', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    limite = request.GET.get('limite', '50')

    mouvements = get_mouvements_filtres(article, type_mouvement, date_debut, date_fin, limite)

    # 30 derniers mouvements pour le graphe — ordre chronologique
    mouvements_qs = list(article.mouvements.all().order_by('created_at')[:30])

    # Sérialisation JSON pour Chart.js
    graphe_labels = json.dumps([
        timezone.localtime(m.created_at).strftime('%d/%m %H:%M')
        for m in mouvements_qs
    ])
    graphe_data = json.dumps([float(m.stock_apres) for m in mouvements_qs])

    return render(request, 'articles/detail.html', {
        'article': article,
        'mouvements': mouvements,
        'mouvements_graphe': mouvements_qs,
        'graphe_labels': graphe_labels,
        'graphe_data': graphe_data,
        'type_mouvement': type_mouvement,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'limite': limite,
    })


@login_required
def mouvements_csv(request, pk):
    article = get_object_or_404(Article, pk=pk)
    type_mouvement = request.GET.get('type_mouvement', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    limite = request.GET.get('limite', '50')

    mouvements = get_mouvements_filtres(article, type_mouvement, date_debut, date_fin, limite)

    type_label = {
        'entree': 'entrees',
        'sortie': 'sorties',
        'inventaire': 'inventaire',
        '': 'tous_mouvements'
    }.get(type_mouvement, 'mouvements')

    date_export = timezone.now().strftime('%Y%m%d_%H%M')
    filename = f"stock_{article.reference}_{type_label}_{date_export}.csv"

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')

    writer = csv.writer(response, delimiter=';')

    writer.writerow([
        'Date',
        'Reference',
        'Designation',
        'Categorie',
        'Type',
        'Quantite',
        'Unite',
        'Prix achat (XPF)',
        'Valeur (XPF)',
        'Stock avant',
        'Stock apres',
        'Motif',
        'Saisi par',
    ])

    for m in mouvements:
        date_locale = timezone.localtime(m.created_at)
        writer.writerow([
            date_locale.strftime('%d/%m/%Y %H:%M'),
            article.reference,
            article.designation,
            article.categorie.libelle,
            m.get_type_display(),
            str(m.quantite).replace('.', ','),
            article.unite.abreviation,
            str(m.prix_achat).replace('.', ',') if m.prix_achat else '',
            str(m.valeur).replace('.', ','),
            str(m.stock_avant).replace('.', ','),
            str(m.stock_apres).replace('.', ','),
            m.motif or '',
            m.user.get_full_name() or m.user.username,
        ])

    return response


@login_required
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Article {article.designation} créé avec succès.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'articles/form.html', {
        'form': form,
        'titre': 'Nouvel article',
    })


@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, f'Article {article.designation} modifié avec succès.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'articles/form.html', {
        'form': form,
        'titre': f'Modifier {article.designation}',
        'article': article,
    })


@login_required
def mouvement_create(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.article = article
            mouvement.user = request.user
            mouvement.stock_avant = article.stock_actuel

            if mouvement.type == 'entree':
                if mouvement.prix_achat:
                    mouvement.valeur = mouvement.quantite * mouvement.prix_achat
                    valeur_stock_avant = article.valeur_stock
                    nouvelle_valeur = valeur_stock_avant + mouvement.valeur
                    nouveau_stock = article.stock_actuel + mouvement.quantite
                    if nouveau_stock > 0:
                        article.pru_moyen = nouvelle_valeur / nouveau_stock
                    article.valeur_stock = nouvelle_valeur
                article.stock_actuel += mouvement.quantite

            elif mouvement.type == 'sortie':
                mouvement.prix_achat = article.pru_moyen
                mouvement.valeur = mouvement.quantite * mouvement.prix_achat
                article.valeur_stock -= mouvement.valeur
                article.stock_actuel -= mouvement.quantite

            elif mouvement.type == 'inventaire':
                article.stock_actuel = mouvement.quantite
                if article.pru_moyen:
                    article.valeur_stock = article.stock_actuel * article.pru_moyen

            mouvement.stock_apres = article.stock_actuel
            article.save()
            mouvement.save()
            messages.success(request, 'Mouvement de stock enregistré.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = MouvementStockForm()
    return render(request, 'articles/mouvement_form.html', {
        'form': form,
        'article': article,
        'titre': f'Mouvement de stock — {article.designation}',
    })


@login_required
def mouvement_update(request, pk):
    mouvement = get_object_or_404(MouvementStock, pk=pk)
    article = mouvement.article

    if not (request.user.is_staff or request.user.role == 'direction'):
        messages.error(request, 'Accès refusé — modification réservée aux administrateurs.')
        return redirect('articles:detail', pk=article.pk)

    if request.method == 'POST':
        form = MouvementStockForm(request.POST, instance=mouvement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mouvement modifié avec succès.')
            return redirect('articles:detail', pk=article.pk)
    else:
        form = MouvementStockForm(instance=mouvement)

    return render(request, 'articles/mouvement_form.html', {
        'form': form,
        'article': article,
        'mouvement': mouvement,
        'titre': f'Modifier mouvement — {article.designation}',
    })


@login_required
def fournisseur_list(request):
    search = request.GET.get('q', '')
    fournisseurs = Fournisseur.objects.all()
    if search:
        fournisseurs = fournisseurs.filter(
            Q(raison_sociale__icontains=search) |
            Q(email__icontains=search)
        )
    return render(request, 'articles/fournisseur_list.html', {
        'fournisseurs': fournisseurs,
        'search': search,
    })


@login_required
def fournisseur_create(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            fournisseur = form.save()
            messages.success(request, f'Fournisseur {fournisseur.raison_sociale} créé avec succès.')
            return redirect('articles:fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'articles/fournisseur_form.html', {
        'form': form,
        'titre': 'Nouveau fournisseur',
    })


@login_required
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fournisseur {fournisseur.raison_sociale} modifié avec succès.')
            return redirect('articles:fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'articles/fournisseur_form.html', {
        'form': form,
        'titre': f'Modifier {fournisseur.raison_sociale}',
        'fournisseur': fournisseur,
    })