import uuid
from django.db import models


class Dossier(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('devis_envoye', 'Devis envoyé'),
        ('accepte', 'Accepté'),
        ('en_fabrication', 'En fabrication'),
        ('annule', 'Annulé'),
        ('expedie', 'Expédié'),
        ('facture', 'Facturé'),
        ('archive', 'Archivé'),
    ]

    PRIORITES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('tres_urgent', 'Très urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True)
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='dossiers'
    )
    technico_commercial = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='dossiers_tc',
        null=True,
        blank=True
    )
    dossier_parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='retirages'
    )
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    priorite = models.CharField(max_length=20, choices=PRIORITES, default='normal')
    visibilite_client = models.BooleanField(default=False)
    notes_internes = models.TextField(blank=True)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dossier'
        verbose_name_plural = 'Dossiers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} — {self.client.raison_sociale}"


class SpecsTechniques(models.Model):
    TYPES_IMPRESSION = [
        ('offset', 'Offset'),
        ('numerique', 'Numérique'),
        ('serigraphie', 'Sérigraphie'),
        ('autre', 'Autre'),
    ]

    RECTO_VERSO = [
        ('recto', 'Recto'),
        ('recto_verso', 'Recto/Verso'),
    ]

    PELLICULAGE = [
        ('aucun', 'Aucun'),
        ('brillant', 'Brillant'),
        ('mat', 'Mat'),
        ('soft_touch', 'Soft Touch'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.OneToOneField(
        Dossier,
        on_delete=models.CASCADE,
        related_name='specs'
    )
    format_final = models.CharField(max_length=50, blank=True)
    format_ouvert = models.CharField(max_length=50, blank=True)
    nb_pages = models.PositiveIntegerField(default=1)
    type_impression = models.CharField(max_length=20, choices=TYPES_IMPRESSION, blank=True)
    recto_verso = models.CharField(max_length=20, choices=RECTO_VERSO, default='recto')
    pelliculage = models.CharField(max_length=20, choices=PELLICULAGE, default='aucun')
    facon = models.CharField(max_length=255, blank=True)
    support = models.CharField(max_length=255, blank=True)
    grammage = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Specs techniques'
        verbose_name_plural = 'Specs techniques'

    def __str__(self):
        return f"Specs — {self.dossier.numero}"


class Tirage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='tirages'
    )
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_selectionne = models.BooleanField(default=False)
    marge_estimee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    marge_reelle = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    imposition_json = models.JSONField(null=True, blank=True)
    imposition_svg = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tirage'
        verbose_name_plural = 'Tirages'
        ordering = ['quantite']

    def __str__(self):
        return f"{self.dossier.numero} — {self.quantite} ex"


class LigneArticle(models.Model):
    TYPES = [
        ('matiere', 'Matière'),
        ('consommable', 'Consommable'),
        ('sous_traitance', 'Sous-traitance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tirage = models.ForeignKey(
        Tirage,
        on_delete=models.CASCADE,
        related_name='lignes_articles'
    )
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.PROTECT,
        related_name='lignes_dossiers'
    )
    type = models.CharField(max_length=20, choices=TYPES, default='matiere')
    quantite = models.DecimalField(max_digits=10, decimal_places=3)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Ligne article'
        verbose_name_plural = 'Lignes articles'

    def __str__(self):
        return f"{self.article.designation} — {self.quantite} {self.article.unite}"

    @property
    def montant(self):
        return self.quantite * self.prix_unitaire


class CoutMachine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tirage = models.ForeignKey(
        Tirage,
        on_delete=models.CASCADE,
        related_name='couts_machines'
    )
    machine = models.ForeignKey(
        'planning.Machine',
        on_delete=models.PROTECT,
        related_name='couts'
    )
    taux_horaire = models.ForeignKey(
        'planning.TauxHoraire',
        on_delete=models.PROTECT,
        related_name='couts_machines'
    )
    duree_estimee_h = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    duree_reelle_h = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Coût machine'
        verbose_name_plural = 'Coûts machines'

    def __str__(self):
        return f"{self.machine.nom} — {self.tirage.dossier.numero}"

    @property
    def cout_estime(self):
        return self.duree_estimee_h * self.taux_horaire.taux

    @property
    def cout_reel(self):
        if self.duree_reelle_h:
            return self.duree_reelle_h * self.taux_horaire.taux
        return None


class CoutOperateur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tirage = models.ForeignKey(
        Tirage,
        on_delete=models.CASCADE,
        related_name='couts_operateurs'
    )
    operateur = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='couts_operateurs'
    )
    taux_horaire = models.ForeignKey(
        'planning.TauxHoraire',
        on_delete=models.PROTECT,
        related_name='couts_operateurs'
    )
    duree_estimee_h = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    duree_reelle_h = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = 'Coût opérateur'
        verbose_name_plural = 'Coûts opérateurs'

    def __str__(self):
        return f"{self.operateur.get_full_name()} — {self.tirage.dossier.numero}"

    @property
    def cout_estime(self):
        return self.duree_estimee_h * self.taux_horaire.taux

    @property
    def cout_reel(self):
        if self.duree_reelle_h:
            return self.duree_reelle_h * self.taux_horaire.taux
        return None


class FichierDossier(models.Model):
    TYPES = [
        ('bat', 'BAT'),
        ('visuel', 'Visuel'),
        ('bon_a_tirer', 'Bon à tirer'),
        ('autre', 'Autre'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        Dossier,
        on_delete=models.CASCADE,
        related_name='fichiers'
    )
    type = models.CharField(max_length=20, choices=TYPES)
    nom = models.CharField(max_length=255)
    fichier = models.FileField(upload_to='dossiers/fichiers/')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='fichiers_uploades'
    )

    class Meta:
        verbose_name = 'Fichier dossier'
        verbose_name_plural = 'Fichiers dossiers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_display()} — {self.nom} — {self.dossier.numero}"