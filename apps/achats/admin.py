from django.contrib import admin
from .models import BonCommande, LigneBonCommande


class LigneBonCommandeInline(admin.TabularInline):
    model = LigneBonCommande
    extra = 1


@admin.register(BonCommande)
class BonCommandeAdmin(admin.ModelAdmin):
    list_display = ['numero', 'fournisseur', 'demandeur', 'validateur', 'statut', 'date', 'date_validation']
    list_filter = ['statut']
    search_fields = ['numero', 'fournisseur__raison_sociale']
    ordering = ['-date']
    inlines = [LigneBonCommandeInline]