from django.contrib import admin
from .models import BonLivraison, LigneLivraison


class LigneLivraisonInline(admin.TabularInline):
    model = LigneLivraison
    extra = 1


@admin.register(BonLivraison)
class BonLivraisonAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'dossier', 'date', 'type_transport', 'statut']
    list_filter = ['statut', 'type_transport']
    search_fields = ['numero', 'client__raison_sociale']
    ordering = ['-date']
    inlines = [LigneLivraisonInline]