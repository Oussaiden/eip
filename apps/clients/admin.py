from django.contrib import admin
from .models import Client, Contact, AdresseLivraison


class ContactInline(admin.TabularInline):
    model = Contact
    extra = 1


class AdresseLivraisonInline(admin.TabularInline):
    model = AdresseLivraison
    extra = 1


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['raison_sociale', 'email', 'telephone', 'actif', 'created_at']
    list_filter = ['actif']
    search_fields = ['raison_sociale', 'email', 'siret']
    ordering = ['raison_sociale']
    inlines = [ContactInline, AdresseLivraisonInline]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prenom', 'client', 'email', 'telephone', 'telephone_mobile', 'is_principal']
    list_filter = ['is_principal']
    search_fields = ['nom', 'prenom', 'email', 'client__raison_sociale']


@admin.register(AdresseLivraison)
class AdresseLivraisonAdmin(admin.ModelAdmin):
    list_display = ['libelle', 'client', 'ville', 'pays', 'is_default']
    list_filter = ['pays', 'is_default']
    search_fields = ['libelle', 'ville', 'client__raison_sociale']
