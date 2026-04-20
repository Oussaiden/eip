from django.contrib import admin
from .models import ArticleStock, ArticleService, Fournisseur, ArticleFournisseur, MouvementStock


class ArticleFournisseurInline(admin.TabularInline):
    model = ArticleFournisseur
    extra = 1


@admin.register(ArticleStock)
class ArticleStockAdmin(admin.ModelAdmin):
    inlines = [ArticleFournisseurInline]
    list_display = ['reference', 'designation', 'categorie', 'unite', 'stock_actuel', 'seuil_minimum', 'actif']
    list_filter = ['categorie', 'sections', 'actif']
    search_fields = ['reference', 'designation']
    filter_horizontal = ['sections']

    def stock_bas(self, obj):
        return obj.stock_bas
    stock_bas.boolean = True
    stock_bas.short_description = 'Stock bas'


@admin.register(ArticleService)
class ArticleServiceAdmin(admin.ModelAdmin):
    list_display = ['reference', 'designation', 'categorie', 'unite', 'prix_vente_ht', 'actif']
    list_filter = ['categorie', 'sections', 'actif']
    search_fields = ['reference', 'designation']
    filter_horizontal = ['sections']


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['raison_sociale', 'email', 'telephone', 'delai_livraison_jours', 'actif']
    list_filter = ['actif']
    search_fields = ['raison_sociale', 'email']


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ['article', 'type', 'quantite', 'stock_avant', 'stock_apres', 'user', 'created_at']
    list_filter = ['type']
    search_fields = ['article__designation', 'user__username']
    readonly_fields = ['stock_avant', 'stock_apres', 'created_at']
