import uuid
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
    nom = models.CharField(max_length=100)
    type = models.ForeignKey(
        'parametres.TypeMachine',
        on_delete=models.PROTECT,
        related_name='machines'
    )
    taux_horaire = models.ForeignKey(
        TauxHoraire,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='machines'
    )
    actif = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Machine'
        verbose_name_plural = 'Machines'
        ordering = ['type__libelle', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.type.libelle})"


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