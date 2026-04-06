import uuid
from django.db import models


class TGC(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=20, unique=True)
    libelle = models.CharField(max_length=100)
    taux = models.DecimalField(max_digits=5, decimal_places=2)
    actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'TGC'
        verbose_name_plural = 'TGC'
        ordering = ['taux']

    def __str__(self):
        return self.libelle


class Categorie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Catégorie article'
        verbose_name_plural = 'Catégories articles'
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


class Unite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=100, unique=True)
    abreviation = models.CharField(max_length=20)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Unité'
        verbose_name_plural = 'Unités'
        ordering = ['libelle']

    def __str__(self):
        return f"{self.libelle} ({self.abreviation})"


class TypeLigneDossier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Type ligne dossier'
        verbose_name_plural = 'Types ligne dossier'
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


class ModePaiement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Mode de paiement'
        verbose_name_plural = 'Modes de paiement'
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


class TypeTransport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Type de transport'
        verbose_name_plural = 'Types de transport'
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


class TypeMachine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    libelle = models.CharField(max_length=100, unique=True)
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Type de machine'
        verbose_name_plural = 'Types de machine'
        ordering = ['libelle']

    def __str__(self):
        return self.libelle


class NumerotationDocument(models.Model):
    TYPE_CHOICES = [
        ('devis', 'Devis'),
        ('dossier', 'Dossier'),
        ('facture', 'Facture'),
        ('avoir', 'Avoir'),
        ('livraison', 'Bon de livraison'),
        ('commande', 'Bon de commande'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type_doc = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    prefixe = models.CharField(max_length=10, blank=True, default='')
    millesime = models.CharField(max_length=4, blank=True, default='')
    separateur = models.CharField(max_length=2, blank=True, default='-')
    longueur = models.PositiveIntegerField(default=5)
    numero_courant = models.PositiveIntegerField(default=1)
    reset_annuel = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Numérotation document'
        verbose_name_plural = 'Numérotations documents'
        ordering = ['type_doc']

    def __str__(self):
        return f"{self.get_type_doc_display()} — {self.prochain_numero()}"

    def prochain_numero(self):
        parts = []
        if self.prefixe:
            parts.append(self.prefixe)
        if self.millesime:
            parts.append(self.millesime)
        parts.append(str(self.numero_courant).zfill(self.longueur))
        return self.separateur.join(parts)

    def incrementer(self):
        numero = self.prochain_numero()
        self.numero_courant += 1
        self.save()
        return numero


class Parametre(models.Model):
    TYPES = [
        ('texte', 'Texte'),
        ('decimal', 'Décimal'),
        ('entier', 'Entier'),
        ('booleen', 'Booléen'),
        ('email', 'Email'),
        ('url', 'URL'),
    ]

    CATEGORIES = [
        ('general', 'Général'),
        ('fiscal', 'Fiscal'),
        ('machine', 'Machine'),
        ('operateur', 'Opérateur'),
        ('email', 'Email'),
        ('impression', 'Impression'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cle = models.CharField(max_length=100, unique=True)
    libelle = models.CharField(max_length=255)
    valeur = models.TextField()
    type = models.CharField(max_length=20, choices=TYPES, default='texte')
    categorie = models.CharField(max_length=20, choices=CATEGORIES, default='general')
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paramètre'
        verbose_name_plural = 'Paramètres'
        ordering = ['categorie', 'libelle']

    def __str__(self):
        return f"{self.libelle} ({self.cle})"