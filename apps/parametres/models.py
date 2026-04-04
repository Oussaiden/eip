import uuid
from django.db import models


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

    def valeur_typee(self):
        if self.type == 'decimal':
            return float(self.valeur)
        if self.type == 'entier':
            return int(self.valeur)
        if self.type == 'booleen':
            return self.valeur.lower() in ('true', '1', 'oui')
        return self.valeur
