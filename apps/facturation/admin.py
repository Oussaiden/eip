from django.contrib import admin
from .models import Facture


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero', 'dossier', 'mode', 'montant_ttc', 'statut', 'date_emission', 'date_echeance']
    list_filter = ['statut', 'mode']
    search_fields = ['numero', 'dossier__numero', 'dossier__client__raison_sociale']
    ordering = ['-created_at']
