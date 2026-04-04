from django.contrib import admin
from .models import Parametre


@admin.register(Parametre)
class ParametreAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'cle', 'valeur', 'type', 'categorie', 'updated_at']
    list_filter = ['categorie', 'type']
    search_fields = ['cle', 'libelle']
    ordering = ['categorie', 'libelle']
