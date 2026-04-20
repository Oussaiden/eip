import uuid
from decimal import Decimal
from django.db import models
from django.utils import timezone


def generer_numero(type_doc):
    from apps.parametres.models import NumerotationDocument
    try:
        config = NumerotationDocument.objects.get(type_doc=type_doc)
        return config.incrementer()
    except NumerotationDocument.DoesNotExist:
        return f"{type_doc.upper()}-{uuid.uuid4().hex[:8].upper()}"


class Devis(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True, blank=True)
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='devis')
    date = models.DateField(default=timezone.now)
    date_validite = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    urgent = models.BooleanField(default=False, verbose_name='Urgent')
    description = models.TextField(blank=True)
    format = models.CharField(max_length=100, blank=True, verbose_name='Format')
    papier = models.CharField(max_length=200, blank=True, verbose_name='Papier')
    notes = models.TextField(blank=True)
    remise_globale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='devis_crees')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Devis'
        verbose_name_plural = 'Devis'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} — {self.client.raison_sociale}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = generer_numero('devis')
        super().save(*args, **kwargs)

    def recalculer(self):
        # Le total du devis = variante acceptée si elle existe
        # sinon = max des variantes (la plus chère)
        # En tout cas on ne les additionne PAS
        variantes = self.variantes.filter(is_deleted=False)
        variante_acceptee = variantes.filter(statut='accepte').first()
        if variante_acceptee:
            self.ht = variante_acceptee.ht
            self.tgc = variante_acceptee.tgc
            self.ttc = variante_acceptee.ttc
        elif variantes.exists():
            # Pas de variante acceptée — on prend la première
            v = variantes.first()
            self.ht = v.ht
            self.tgc = v.tgc
            self.ttc = v.ttc
        else:
            self.ht = Decimal('0')
            self.tgc = Decimal('0')
            self.ttc = Decimal('0')
        self.save()


class VarianteDevis(models.Model):
    STATUTS = [
        ('brouillon', 'Brouillon'),
        ('envoye', 'Envoyé'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('annule', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='variantes')
    libelle = models.CharField(max_length=100)
    quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Quantité')
    statut = models.CharField(max_length=20, choices=STATUTS, default='brouillon')
    remise_globale = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gain = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ordre = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Variante devis'
        verbose_name_plural = 'Variantes devis'
        ordering = ['ordre']

    def __str__(self):
        return f"{self.devis.numero} — {self.libelle}"

    def recalculer(self):
        lignes = self.lignes.filter(type__in=['article', 'service', 'libre'])
        ht_avant_remise = sum(l.ht for l in lignes) or Decimal('0')
        self.ht = ht_avant_remise * (1 - self.remise_globale / 100)
        self.tgc = sum(l.tgc for l in lignes) or Decimal('0')
        self.ttc = self.ht + self.tgc
        self.gain = self.ht - (sum(l.pru * l.qte for l in lignes if l.pru) or Decimal('0'))
        self.save()
        self.devis.recalculer()


class LigneDevis(models.Model):
    TYPES = [
        ('article', 'Article stock'),
        ('service', 'Service'),
        ('machine', 'Machine'),
        ('libre', 'Ligne libre'),
        ('texte', 'Texte'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variante = models.ForeignKey(VarianteDevis, on_delete=models.CASCADE, related_name='lignes', null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPES, default='libre')
    section = models.ForeignKey(
        'parametres.Section',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lignes_devis',
        verbose_name='Section'
    )
    article = models.ForeignKey('articles.ArticleStock', on_delete=models.PROTECT, null=True, blank=True, related_name='lignes_devis')
    article_service = models.ForeignKey('articles.ArticleService', on_delete=models.PROTECT, null=True, blank=True, related_name='lignes_devis')
    machine = models.ForeignKey('planning.Machine', on_delete=models.PROTECT, null=True, blank=True, related_name='lignes_devis')
    designation = models.CharField(max_length=255, blank=True)
    qte = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pru = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taux_tgc = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    ht = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tgc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gain = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Ligne devis'
        verbose_name_plural = 'Lignes devis'
        ordering = ['ordre']

    def __str__(self):
        return f"{self.designation} — {self.variante}"

    def save(self, *args, **kwargs):
        if self.type == 'machine' and self.machine and self.qte > 0:
            self.pu = self.machine.calculer_pu(self.qte)
            self.pru = self.machine.calculer_pu(self.qte)
        if self.type in ['article', 'service', 'machine', 'libre']:
            base = self.qte * self.pu
            self.ht = base * (1 - self.remise / 100)
            self.tgc = self.ht * self.taux_tgc / 100
            self.ttc = self.ht + self.tgc
            self.gain = self.ht - (self.pru * self.qte)
        else:
            self.ht = Decimal('0')
            self.tgc = Decimal('0')
            self.ttc = Decimal('0')
            self.gain = Decimal('0')
        super().save(*args, **kwargs)
        if self.variante and self.type != 'texte':
            self.variante.recalculer()


class Dossier(models.Model):
    STATUTS = [
        ('en_fabrication', 'En fabrication'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
        ('livre', 'Livré'),
    ]

    PRIORITES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
        ('tres_urgent', 'Très urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True, blank=True)
    variante = models.OneToOneField(VarianteDevis, on_delete=models.PROTECT, null=True, blank=True, related_name='dossier')
    client = models.ForeignKey('clients.Client', on_delete=models.PROTECT, related_name='dossiers')
    date = models.DateField(default=timezone.now)
    date_livraison = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_fabrication')
    priorite = models.CharField(max_length=20, choices=PRIORITES, default='normal')
    visible_client = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    notes_fab = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='dossiers_crees')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Dossier'
        verbose_name_plural = 'Dossiers'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.numero} — {self.client.raison_sociale}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = generer_numero('dossier')
        super().save(*args, **kwargs)

    @property
    def gain_prevu(self):
        pv_ht = self.variante.ht if self.variante else Decimal('0')
        pr_prevu = sum(l.pru * l.qte_prevue for l in self.lignes.all()) or Decimal('0')
        return pv_ht - pr_prevu

    @property
    def gain_reel(self):
        pv_ht = self.variante.ht if self.variante else Decimal('0')
        pr_reel = sum(l.pru * (l.qte_consommee or Decimal('0')) for l in self.lignes.all()) or Decimal('0')
        return pv_ht - pr_reel

    @property
    def pr_prevu_par_type(self):
        result = {}
        for ligne in self.lignes.all():
            type_lib = ligne.type.libelle
            result[type_lib] = result.get(type_lib, Decimal('0')) + (ligne.pru * ligne.qte_prevue)
        return result

    @property
    def pr_reel_par_type(self):
        result = {}
        for ligne in self.lignes.all():
            type_lib = ligne.type.libelle
            result[type_lib] = result.get(type_lib, Decimal('0')) + (ligne.pru * (ligne.qte_consommee or Decimal('0')))
        return result


class LigneDossier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name='lignes')
    article = models.ForeignKey('articles.ArticleStock', on_delete=models.PROTECT, null=True, blank=True, related_name='lignes_dossiers')
    article_service = models.ForeignKey('articles.ArticleService', on_delete=models.PROTECT, null=True, blank=True, related_name='lignes_dossiers')
    type = models.ForeignKey('parametres.TypeLigneDossier', on_delete=models.PROTECT, related_name='lignes_dossier')
    designation = models.CharField(max_length=255)
    qte_prevue = models.DecimalField(max_digits=10, decimal_places=2)
    qte_consommee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pru = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    pr = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = 'Ligne dossier'
        verbose_name_plural = 'Lignes dossier'

    def __str__(self):
        return f"{self.designation} — {self.dossier.numero}"

    def save(self, *args, **kwargs):
        self.pr = self.pru * (self.qte_consommee or self.qte_prevue)
        super().save(*args, **kwargs)


class PointageAtelier(models.Model):
    STATUTS = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(Dossier, on_delete=models.PROTECT, related_name='pointages')
    operateur = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='pointages')
    ligne_dossier = models.ForeignKey(LigneDossier, on_delete=models.PROTECT, related_name='pointages', null=True, blank=True)
    type_tache = models.ForeignKey('parametres.TypeLigneDossier', on_delete=models.PROTECT, related_name='pointages')
    qte_prevue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    qte_reelle = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    debut = models.DateTimeField(auto_now_add=True)
    fin = models.DateTimeField(null=True, blank=True)
    duree_minutes = models.PositiveIntegerField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUTS, default='en_cours')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pointage atelier'
        verbose_name_plural = 'Pointages atelier'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.dossier.numero} — {self.type_tache.libelle} — {self.operateur.username}"

    def terminer(self, qte_reelle, notes=''):
        import math
        qte_reelle = Decimal(str(qte_reelle))
        self.qte_reelle = qte_reelle
        self.fin = timezone.now()
        self.notes = notes
        self.statut = 'termine'
        delta = self.fin - self.debut
        self.duree_minutes = math.ceil(delta.total_seconds() / 60)
        self.save()

        if self.ligne_dossier:
            ligne = self.ligne_dossier
            ancien = ligne.qte_consommee or Decimal('0')
            ligne.qte_consommee = ancien + qte_reelle
            ligne.save()

            if ligne.article:
                from apps.articles.models import MouvementStock
                article = ligne.article
                valeur = qte_reelle * article.pru_moyen
                mouvement = MouvementStock(
                    article=article,
                    user=self.operateur,
                    dossier=self.dossier,
                    type='sortie',
                    quantite=qte_reelle,
                    prix_achat=article.pru_moyen,
                    valeur=valeur,
                    stock_avant=article.stock_actuel,
                    stock_apres=article.stock_actuel - qte_reelle,
                    motif=f"Dossier {self.dossier.numero} — {self.type_tache.libelle}",
                )
                article.stock_actuel -= qte_reelle
                article.valeur_stock -= valeur
                article.save()
                mouvement.stock_apres = article.stock_actuel
                mouvement.save()