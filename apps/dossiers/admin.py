from django.contrib import admin
from .models import Devis, VarianteDevis, LigneDevis, Dossier, LigneDossier, PointageAtelier


class VarianteDevisInline(admin.TabularInline):
    model = VarianteDevis
    extra = 1


class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 1


class LigneDossierInline(admin.TabularInline):
    model = LigneDossier
    extra = 1


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'date', 'statut', 'ht', 'ttc']
    list_filter = ['statut']
    search_fields = ['numero', 'client__raison_sociale']
    ordering = ['-created_at']
    inlines = [VarianteDevisInline]


@admin.register(VarianteDevis)
class VarianteDevisAdmin(admin.ModelAdmin):
    list_display = ['devis', 'libelle', 'statut', 'ht', 'ttc', 'gain']
    list_filter = ['statut']
    search_fields = ['devis__numero', 'libelle']
    inlines = [LigneDevisInline]


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'date', 'statut', 'priorite', 'date_livraison']
    list_filter = ['statut', 'priorite']
    search_fields = ['numero', 'client__raison_sociale']
    ordering = ['-created_at']
    inlines = [LigneDossierInline]


@admin.register(PointageAtelier)
class PointageAtelierAdmin(admin.ModelAdmin):
    list_display = ['dossier', 'operateur', 'type_tache', 'qte_prevue', 'qte_reelle', 'statut', 'debut', 'fin']
    list_filter = ['statut']
    search_fields = ['dossier__numero', 'operateur__username']
    ordering = ['-created_at']