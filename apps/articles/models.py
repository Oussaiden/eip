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
    CATEGORIES = [
        ('papier', 'Papier'),
        ('encre', 'Encre'),
        ('consommable', 'Consommable'),
        ('autre', 'Autre'),
    ]

    UNITES = [
        ('kg', 'Kilogramme'),
        ('g', 'Gramme'),
        ('l', 'Litre'),
        ('ml', 'Millilitre'),
        ('m2', 'Mètre carré'),
        ('feuille', 'Feuille'),
        ('unite', 'Unité'),
        ('boite', 'Boîte'),
        ('rouleau', 'Rouleau'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=100, unique=True)
    designation = models.CharField(max_length=255)
    categorie = models.CharField(max_length=20, choices=CATEGORIES)
    unite = models.CharField(max_length=20, choices=UNITES)
    stock_actuel = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    seuil_minimum = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    notes = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['categorie', 'designation']

    def __str__(self):
        return f"{self.reference} — {self.designation}"

    @property
    def stock_bas(self):
        return self.stock_actuel <= self.seuil_minimum


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
    quantite = models.DecimalField(max_digits=10, decimal_places=3)
    stock_avant = models.DecimalField(max_digits=10, decimal_places=3)
    stock_apres = models.DecimalField(max_digits=10, decimal_places=3)
    motif = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mouvement de stock'
        verbose_name_plural = 'Mouvements de stock'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} — {self.article.designation} — {self.quantite} {self.article.unite}"