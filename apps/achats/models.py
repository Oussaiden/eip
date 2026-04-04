import uuid
from django.db import models


class BonCommande(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('en_attente_validation', 'En attente de validation'),
        ('valide', 'Validé'),
        ('envoye', 'Envoyé'),
        ('recu', 'Reçu'),
        ('annule', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True)
    fournisseur = models.ForeignKey(
        'articles.Fournisseur',
        on_delete=models.PROTECT,
        related_name='bons_commande'
    )
    demandeur = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='bons_commande_demandes'
    )
    validateur = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bons_commande_valides'
    )
    statut = models.CharField(max_length=30, choices=STATUTS, default='brouillon')
    date_demande = models.DateField(auto_now_add=True)
    date_validation = models.DateField(null=True, blank=True)
    date_livraison_prevue = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Bon de commande'
        verbose_name_plural = 'Bons de commande'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} — {self.fournisseur.raison_sociale}"


class LigneBonCommande(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bon_commande = models.ForeignKey(
        BonCommande,
        on_delete=models.CASCADE,
        related_name='lignes'
    )
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.PROTECT,
        related_name='lignes_commande'
    )
    quantite = models.DecimalField(max_digits=10, decimal_places=3)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_recue = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    class Meta:
        verbose_name = 'Ligne bon de commande'
        verbose_name_plural = 'Lignes bon de commande'

    def __str__(self):
        return f"{self.article.designation} — {self.quantite} {self.article.unite}"

    @property
    def montant(self):
        return self.quantite * self.prix_unitaire

    @property
    def quantite_restante(self):
        return self.quantite - self.quantite_recue
