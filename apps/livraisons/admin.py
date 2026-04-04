from django.contrib import admin
from .models import BonLivraison, LigneLivraison


class LigneLivraisonInline(admin.TabularInline):
    model = LigneLivraison
    extra = 1


@admin.register(BonLivraison)
class BonLivraisonAdmin(admin.ModelAdmin):
    list_display = ['dossier', 'type_transport', 'transporteur', 'statut', 'date_expedition', 'date_livraison_reelle']
    list_filter = ['statut', 'type_transport']
    search_fields = ['dossier__numero', 'transporteur', 'numero_suivi']
    ordering = ['-created_at']
    inlines = [LigneLivraisonInline]
