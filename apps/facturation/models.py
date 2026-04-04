import uuid
from django.db import models


class Facture(models.Model):
    MODES = [
        ('commande', 'À la commande'),
        ('livraison', 'À la livraison'),
        ('acompte', 'Acompte'),
    ]

    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('emise', 'Émise'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
        ('avoir', 'Avoir'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.PROTECT,
        related_name='factures'
    )
    numero = models.CharField(max_length=50, unique=True)
    mode = models.CharField(max_length=20, choices=MODES)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tva = models.DecimalField(max_digits=5, decimal_places=2, default=11)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2)
    cout_transport = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    date_emission = models.DateField(null=True, blank=True)
    date_echeance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='factures_creees'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} — {self.dossier.client.raison_sociale} — {self.montant_ttc} XPF"
