from django.contrib import admin
from .models import Article, Fournisseur, ArticleFournisseur, MouvementStock


class ArticleFournisseurInline(admin.TabularInline):
    model = ArticleFournisseur
    extra = 1


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['reference', 'designation', 'categorie', 'unite', 'stock_actuel', 'seuil_minimum', 'actif']
    list_filter = ['categorie', 'sections', 'actif']
    search_fields = ['reference', 'designation']
    filter_horizontal = ['sections']
    inlines = [ArticleFournisseurInline]

    def stock_bas(self, obj):
        return obj.stock_bas
    stock_bas.boolean = True
    stock_bas.short_description = 'Stock bas'


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