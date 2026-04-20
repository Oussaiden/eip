import uuid
from decimal import Decimal
from django.db import models


class TauxHoraire(models.Model):
    TYPE_CHOICES = [
        ('machine', 'Machine'),
        ('operateur', 'Opérateur'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    libelle = models.CharField(max_length=100)
    taux = models.DecimalField(max_digits=8, decimal_places=2)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Taux horaire'
        verbose_name_plural = 'Taux horaires'
        ordering = ['-date_debut']

    def __str__(self):
        return f"{self.libelle} — {self.taux} XPF/h"


class Machine(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reference = models.CharField(max_length=100, unique=True, blank=True)
    nom = models.CharField(max_length=255)
    type = models.ForeignKey(
        'parametres.TypeMachine',
        on_delete=models.PROTECT,
        related_name='machines'
    )
    taux_horaire = models.ForeignKey(
        TauxHoraire,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name='machines'
    )
    description = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    # Format papier (mm)
    format_min_largeur = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='Larg. min (mm)')
    format_min_hauteur = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='Haut. min (mm)')
    format_max_largeur = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='Larg. max (mm)')
    format_max_hauteur = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='Haut. max (mm)')

    # Caractéristiques techniques
    nb_couleurs = models.PositiveIntegerField(default=4, verbose_name='Nb couleurs')
    vitesse_max = models.DecimalField(max_digits=8, decimal_places=1, default=0, verbose_name='Vitesse max (t/min)')
    recto_verso = models.BooleanField(default=False, verbose_name='Recto-verso')
    vitesse_recto_verso = models.DecimalField(max_digits=8, decimal_places=1, null=True, blank=True, verbose_name='Vitesse R/V (t/min)')

    # Temps par job (minutes)
    temps_mise_en_oeuvre = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='Mise en œuvre (min)')
    temps_calage = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='Calage (min)')
    temps_nettoyage = models.DecimalField(max_digits=6, decimal_places=1, default=0, verbose_name='Nettoyage (min)')

    # Coûts horaires (XPF/h)
    cout_nrj_heure = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Coût NRJ (XPF/h)')
    cout_amortissement_heure = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Coût amortissement (XPF/h)')
    cout_entretien_heure = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Coût entretien (XPF/h)')

    # Qualité
    taux_gache = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Taux de gâche (%)')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Machine'
        verbose_name_plural = 'Machines'
        ordering = ['type__libelle', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.type.libelle})"

    @property
    def cout_heure(self):
        return self.cout_nrj_heure + self.cout_amortissement_heure + self.cout_entretien_heure

    @property
    def cout_fixe_job(self):
        temps_total = self.temps_calage + self.temps_nettoyage + self.temps_mise_en_oeuvre
        return self.cout_heure * temps_total / 60

    @property
    def cout_par_impression(self):
        if self.vitesse_max and self.vitesse_max > 0:
            return self.cout_heure / self.vitesse_max / 60
        return Decimal('0')

    def calculer_cout_total(self, nb_impressions):
        nb = Decimal(str(nb_impressions))
        cout_variable = self.cout_par_impression * nb * (1 + self.taux_gache / 100)
        return self.cout_fixe_job + cout_variable

    def calculer_pu(self, nb_impressions):
        nb = Decimal(str(nb_impressions))
        if nb > 0:
            return round(self.calculer_cout_total(nb) / nb, 4)
        return Decimal('0')

    @property
    def cout_pour_mille(self):
        return round(self.cout_par_impression * 1000, 2)

    @property
    def format_min(self):
        if self.format_min_largeur and self.format_min_hauteur:
            return f"{self.format_min_largeur:.0f} × {self.format_min_hauteur:.0f} mm"
        return "—"

    @property
    def format_max(self):
        if self.format_max_largeur and self.format_max_hauteur:
            return f"{self.format_max_largeur:.0f} × {self.format_max_hauteur:.0f} mm"
        return "—"


class PlanningCreneau(models.Model):
    STATUTS = [
        ('planifie', 'Planifié'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dossier = models.ForeignKey(
        'dossiers.Dossier',
        on_delete=models.CASCADE,
        related_name='creneaux'
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name='creneaux'
    )
    operateur = models.ForeignKey(
        'accounts.User',
        on_delete=models.PROTECT,
        related_name='creneaux'
    )
    debut = models.DateTimeField()
    fin = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUTS, default='planifie')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Créneau planning'
        verbose_name_plural = 'Créneaux planning'
        ordering = ['debut']

    def __str__(self):
        return f"{self.dossier} — {self.machine.nom} — {self.debut.strftime('%d/%m/%Y %H:%M')}"
