import uuid
from django.db import models


class Fournisseur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raison_sociale = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=255, blank=True)
    ville = models.CharField(max_length=100, blank=True)
    pays = models.CharField(max_length=100, blank=True)
    delai_livraison_jours = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Fournisseur'
        verbose_name_plural = 'Fournisseurs'
        ordering = ['raison_sociale']

    def __str__(self):
        return self.raison_sociale


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=100, unique=True)
    designation = models.CharField(max_length=255)
    categorie = models.ForeignKey(
        'parametres.Categorie',
        on_delete=models.PROTECT,
        related_name='articles'
    )
    unite = models.ForeignKey(
        'parametres.Unite',
        on_delete=models.PROTECT,
        related_name='articles'
    )
    tgc_achat = models.ForeignKey(
        'parametres.TGC',
        on_delete=models.PROTECT,
        related_name='articles_achat',
        null=True,
        blank=True,
        verbose_name='TGC achat'
    )
    tgc_vente = models.ForeignKey(
        'parametres.TGC',
        on_delete=models.PROTECT,
        related_name='articles_vente',
        null=True,
        blank=True,
        verbose_name='TGC vente'
    )
    prix_vente_ht = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Prix de vente HT'
    )
    stock_actuel = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seuil_minimum = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valeur_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pru_moyen = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['categorie__libelle', 'designation']

    def __str__(self):
        return f"{self.reference} — {self.designation}"

    @property
    def stock_bas(self):
        return self.stock_actuel <= self.seuil_minimum

    @property
    def taux_marge(self):
        if self.pru_moyen and self.prix_vente_ht and self.prix_vente_ht > 0:
            return round((self.prix_vente_ht - self.pru_moyen) / self.prix_vente_ht * 100, 2)
        return 0


class ArticleFournisseur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='fournisseurs'
    )
    fournisseur = models.ForeignKey(
        Fournisseur,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    reference_fournisseur = models.CharField(max_length=100, blank=True)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    is_prefere = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article fournisseur'
        verbose_name_plural = 'Articles fournisseurs'
        unique_together = ['article', 'fournisseur']

    def __str__(self):
        return f"{self.article.designation} — {self.fournisseur.raison_sociale}"


class MouvementStock(models.Model):
    TYPES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('inventaire', 'Inventaire'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    article = models.ForeignKey(
        Article,
        on_delete=models.PROTECT,
        related_name='mouvements'
    )
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='mouvements_stock'
    )
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mouvements_stock'
    )
    type = models.CharField(max_length=20, choices=TYPES)
    quantite = models.DecimalField(max_digits=10, decimal_places=2)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valeur = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_avant = models.DecimalField(max_digits=10, decimal_places=2)
    stock_apres = models.DecimalField(max_digits=10, decimal_places=2)
    motif = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} — {self.article.designation} — {self.quantite} {self.article.unite.abreviation}"