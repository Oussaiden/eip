from django.contrib import admin
from .models import Facture, LigneFacture, Avoir, LigneAvoir, Reglement


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1


class LigneAvoirInline(admin.TabularInline):
    model = LigneAvoir
    extra = 1


class ReglementInline(admin.TabularInline):
    model = Reglement
    extra = 1


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'date', 'statut', 'ht', 'ttc', 'solde']
    list_filter = ['statut']
    search_fields = ['numero', 'client__raison_sociale']
    ordering = ['-date']
    inlines = [LigneFactureInline, ReglementInline]


@admin.register(Avoir)
class AvoirAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'date', 'statut', 'ttc']
    list_filter = ['statut']
    search_fields = ['numero', 'client__raison_sociale']
    ordering = ['-date']
    inlines = [LigneAvoirInline]


@admin.register(Reglement)
class ReglementAdmin(admin.ModelAdmin):
    list_display = ['facture', 'date', 'montant', 'mode_paiement', 'reference']
    list_filter = ['mode_paiement']
    search_fields = ['facture__numero', 'reference']
    ordering = ['-date']