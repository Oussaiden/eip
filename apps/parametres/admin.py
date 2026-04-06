from django.contrib import admin
from .models import TGC, Categorie, Unite, TypeLigneDossier, ModePaiement, TypeTransport, TypeMachine, NumerotationDocument, Parametre


@admin.register(TGC)
class TGCAdmin(admin.ModelAdmin):
    list_display = ['code', 'libelle', 'taux', 'actif', 'date_debut', 'date_fin']
    list_filter = ['actif']
    search_fields = ['code', 'libelle']


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'actif']
    list_filter = ['actif']
    search_fields = ['libelle']


@admin.register(Unite)
class UniteAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'abreviation', 'actif']
    list_filter = ['actif']
    search_fields = ['libelle', 'abreviation']


@admin.register(TypeLigneDossier)
class TypeLigneDossierAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'actif']
    list_filter = ['actif']
    search_fields = ['libelle']


@admin.register(ModePaiement)
class ModePaiementAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'actif']
    list_filter = ['actif']
    search_fields = ['libelle']


@admin.register(TypeTransport)
class TypeTransportAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'actif']
    list_filter = ['actif']
    search_fields = ['libelle']


@admin.register(TypeMachine)
class TypeMachineAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'actif']
    list_filter = ['actif']
    search_fields = ['libelle']


@admin.register(NumerotationDocument)
class NumerotationDocumentAdmin(admin.ModelAdmin):
    list_display = ['type_doc', 'prefixe', 'millesime', 'separateur', 'longueur', 'numero_courant', 'reset_annuel', 'updated_at']
    search_fields = ['type_doc', 'prefixe']


@admin.register(Parametre)
class ParametreAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'cle', 'valeur', 'type', 'categorie', 'updated_at']
    list_filter = ['categorie', 'type']
    search_fields = ['cle', 'libelle']
    ordering = ['categorie', 'libelle']