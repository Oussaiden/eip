import uuid
from django.db import models


class BonLivraison(models.Model):
    STATUTS = [
        ('prepare', 'Préparé'),
        ('expedie', 'Expédié'),
        ('livre', 'Livré'),
        ('partiel', 'Partiel'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True)
    dossier = models.ForeignKey('dossiers.Dossier', on_delete=models.PROTECT, related_name='bons_livraison')
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='bons_livraison')
    adresse = models.ForeignKey('clients.AdresseLivraison', on_delete=models.PROTECT, related_name='bons_livraison')
    type_transport = models.ForeignKey('parametres.TypeTransport', on_delete=models.PROTECT, related_name='bons_livraison')
    date = models.DateField()
    transporteur = models.CharField(max_length=100, blank=True)
    no_suivi = models.CharField(max_length=100, blank=True)
    mt_transport = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUTS, default='prepare')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='bons_livraison_crees')

    class Meta:
        verbose_name = 'Bon de livraison'
        verbose_name_plural = 'Bons de livraison'
        ordering = ['-date']

    def __str__(self):
        return f"{self.numero} — {self.client.raison_sociale}"


class LigneLivraison(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bon_livraison = models.ForeignKey(BonLivraison, on_delete=models.CASCADE, related_name='lignes')
    designation = models.CharField(max_length=255)
    qte_prevue = models.DecimalField(max_digits=10, decimal_places=3)
    qte_livree = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    qte_restante = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    class Meta:
        verbose_name = 'Ligne livraison'
        verbose_name_plural = 'Lignes livraison'

    def __str__(self):
        return f"{self.designation} — {self.bon_livraison.numero}"

    def save(self, *args, **kwargs):
        self.qte_restante = self.qte_prevue - self.qte_livree
        super().save(*args, **kwargs)