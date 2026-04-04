from django.contrib import admin
from .models import Machine, TauxHoraire, PlanningCreneau


@admin.register(TauxHoraire)
class TauxHoraireAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'type', 'taux', 'date_debut', 'date_fin']
    list_filter = ['type']
    search_fields = ['libelle']
    ordering = ['-date_debut']


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type', 'taux_horaire', 'actif']
    list_filter = ['type', 'actif']
    search_fields = ['nom']


@admin.register(PlanningCreneau)
class PlanningCreneauAdmin(admin.ModelAdmin):
    list_display = ['dossier', 'machine', 'operateur', 'debut', 'fin', 'statut']
    list_filter = ['statut', 'machine']
    search_fields = ['dossier__numero', 'operateur__username']
    ordering = ['debut']
