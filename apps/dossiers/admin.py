from django.contrib import admin
from .models import Dossier, SpecsTechniques, Tirage, LigneArticle, CoutMachine, CoutOperateur, FichierDossier


class SpecsTechniquesInline(admin.StackedInline):
    model = SpecsTechniques
    extra = 0


class TirageInline(admin.TabularInline):
    model = Tirage
    extra = 1


class FichierDossierInline(admin.TabularInline):
    model = FichierDossier
    extra = 0


@admin.register(Dossier)
class DossierAdmin(admin.ModelAdmin):
    list_display = ['numero', 'client', 'statut', 'priorite', 'technico_commercial', 'date_livraison_prevue', 'created_at']
    list_filter = ['statut', 'priorite']
    search_fields = ['numero', 'client__raison_sociale']
    ordering = ['-created_at']
    inlines = [SpecsTechniquesInline, TirageInline, FichierDossierInline]


@admin.register(Tirage)
class TirageAdmin(admin.ModelAdmin):
    list_display = ['dossier', 'quantite', 'prix_total', 'is_selectionne', 'marge_estimee']
    list_filter = ['is_selectionne']
    search_fields = ['dossier__numero']


@admin.register(FichierDossier)
class FichierDossierAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type', 'dossier', 'uploaded_by', 'created_at']
    list_filter = ['type']
    search_fields = ['nom', 'dossier__numero']
