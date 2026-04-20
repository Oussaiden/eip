from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),

    # Stock
    path('stock/nouveau/', views.stock_create, name='stock_create'),
    path('stock/<uuid:pk>/', views.stock_detail, name='stock_detail'),
    path('stock/<uuid:pk>/modifier/', views.stock_update, name='stock_update'),
    path('stock/<uuid:pk>/mouvement/', views.mouvement_create, name='mouvement'),
    path('stock/<uuid:pk>/mouvements/csv/', views.mouvements_csv, name='mouvements_csv'),
    path('stock/mouvement/<uuid:pk>/modifier/', views.mouvement_update, name='mouvement_update'),

    # Service
    path('service/nouveau/', views.service_create, name='service_create'),
    path('service/<uuid:pk>/', views.service_detail, name='service_detail'),
    path('service/<uuid:pk>/modifier/', views.service_update, name='service_update'),

    # Fournisseurs
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/nouveau/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<uuid:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
]
