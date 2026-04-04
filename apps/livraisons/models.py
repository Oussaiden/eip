import uuid
from django.db import models


class BonLivraison(models.Model):
    TYPES_TRANSPORT = [
        ('transporteur_externe', 'Transporteur externe'),
        ('camion_eip', 'Camion EIP'),
    ]

    STATUTS = [
        ('prepare', 'Préparé'),
        ('expedie', 'Expédié'),
        ('livre', 'Livré'),
        ('partiel', 'Livraison partielle'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.PROTECT,
        related_name='bons_livraison'
    )
    adresse = models.ForeignKey(
        'clients.AdresseLivraison',
        on_delete=models.PROTECT,
        related_name='bons_livraison'
    )
    createur = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='bons_livraison_crees'
    )
    type_transport = models.CharField(max_length=30, choices=TYPES_TRANSPORT)
    transporteur = models.CharField(max_length=100, blank=True)
    chauffeur = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='livraisons_chauffeur'
    )
    numero_suivi = models.CharField(max_length=100, blank=True)
    cout_transport = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_expedition = models.DateField(null=True, blank=True)
    date_livraison_reelle = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='prepare')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bon de livraison'
        verbose_name_plural = 'Bons de livraison'
        ordering = ['-created_at']

    def __str__(self):
        return f"BL — {self.dossier.numero} — {self.get_statut_display()}"


class LigneLivraison(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bon_livraison = models.ForeignKey(
        BonLivraison,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    quantite_prevue = models.PositiveIntegerField()
    quantite_livree = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Ligne de livraison'
        verbose_name_plural = 'Lignes de livraison'

    def __str__(self):
        return f"{self.bon_livraison} — {self.quantite_livree}/{self.quantite_prevue}"

    @property
    def quantite_restante(self):
        return self.quantite_prevue - self.quantite_livree

    @property
    def is_complete(self):
        return self.quantite_livree >= self.quantite_prevue