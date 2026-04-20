import uuid
from django.db import models


class Facture(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('emise', 'Émise'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True)
    dossier = models.ForeignKey('dossiers.Dossier', on_delete=models.PROTECT, related_name='factures')
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='factures')
    date = models.DateField()
    echeance = models.DateField(null=True, blank=True)
    mode_paiement = models.ForeignKey('parametres.ModePaiement', on_delete=models.PROTECT, null=True, blank=True, related_name='factures')
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    mt_regle = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    solde = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='factures_creees')

    class Meta:
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'
        ordering = ['-date']

    def __str__(self):
        return f"{self.numero} — {self.client.raison_sociale}"

    def update_solde(self):
        self.mt_regle = sum(r.montant for r in self.reglements.all())
        self.solde = self.ttc - self.mt_regle
        self.save()


class LigneFacture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey('articles.ArticleStock', on_delete=models.PROTECT, null=True, blank=True, related_name='lignes_factures')
    designation = models.CharField(max_length=255)
    qte = models.DecimalField(max_digits=10, decimal_places=3)
    pu = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tgc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pru = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pr = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Ligne facture'
        verbose_name_plural = 'Lignes facture'
        ordering = ['ordre']

    def __str__(self):
        return f"{self.designation} — {self.facture.numero}"

    def save(self, *args, **kwargs):
        base = self.qte * self.pu
        self.ht = base * (1 - self.remise / 100)
        self.tgc = self.ht * self.taux_tgc / 100
        self.ttc = self.ht + self.tgc
        self.pr = self.pru * self.qte
        super().save(*args, **kwargs)


class Avoir(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('emis', 'Émis'),
        ('annule', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True)
    facture = models.ForeignKey(Facture, on_delete=models.PROTECT, related_name='avoirs')
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='avoirs')
    date = models.DateField()
    motif = models.CharField(max_length=255)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='avoirs_crees')

    class Meta:
        verbose_name = 'Avoir'
        verbose_name_plural = 'Avoirs'
        ordering = ['-date']

    def __str__(self):
        return f"{self.numero} — {self.client.raison_sociale}"


class LigneAvoir(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avoir = models.ForeignKey(Avoir, on_delete=models.CASCADE, related_name='lignes')
    designation = models.CharField(max_length=255)
    qte = models.DecimalField(max_digits=10, decimal_places=3)
    pu = models.DecimalField(max_digits=10, decimal_places=2)
    taux_tgc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Ligne avoir'
        verbose_name_plural = 'Lignes avoir'
        ordering = ['ordre']

    def __str__(self):
        return f"{self.designation} — {self.avoir.numero}"

    def save(self, *args, **kwargs):
        self.ht = self.qte * self.pu
        self.tgc = self.ht * self.taux_tgc / 100
        self.ttc = self.ht + self.tgc
        super().save(*args, **kwargs)


class Reglement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey(Facture, on_delete=models.PROTECT, related_name='reglements')
    mode_paiement = models.ForeignKey('parametres.ModePaiement', on_delete=models.PROTECT, related_name='reglements')
    date = models.DateField()
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True)
    banque = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='reglements_crees')

    class Meta:
        verbose_name = 'Règlement'
        verbose_name_plural = 'Règlements'
        ordering = ['-date']

    def __str__(self):
        return f"{self.facture.numero} — {self.montant} XPF"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.facture.update_solde()