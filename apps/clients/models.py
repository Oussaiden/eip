import uuid
from django.db import models


class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raison_sociale = models.CharField(max_length=255)
    siret = models.CharField(max_length=14, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'
        ordering = ['raison_sociale']

    def __str__(self):
        return self.raison_sociale


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=20, blank=True)
    telephone_mobile = models.CharField(max_length=20, blank=True)
    poste = models.CharField(max_length=100, blank=True)
    is_principal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['-is_principal', 'nom']

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.client.raison_sociale}"


class AdresseLivraison(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='adresses'
    )
    libelle = models.CharField(max_length=100, help_text="Ex: Siège social, Entrepôt Nord...")
    adresse = models.CharField(max_length=255)
    complement = models.CharField(max_length=255, blank=True)
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    pays = models.CharField(max_length=100, default='Nouvelle-Calédonie')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Adresse de livraison'
        verbose_name_plural = 'Adresses de livraison'
        ordering = ['-is_default', 'libelle']

    def __str__(self):
        return f"{self.libelle} — {self.ville} ({self.client.raison_sociale})"