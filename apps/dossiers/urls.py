from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    # Devis
    path('', views.devis_list, name='list'),
    path('nouveau/', views.devis_create, name='create'),
    path('<uuid:pk>/', views.devis_detail, name='detail'),
    path('<uuid:pk>/modifier/', views.devis_update, name='update'),
    path('<uuid:pk>/supprimer/', views.devis_delete, name='delete'),

    # Variantes
    path('<uuid:devis_pk>/variantes/nouvelle/', views.variante_create, name='variante_create'),
    path('variantes/<uuid:pk>/modifier/', views.variante_update, name='variante_update'),
    path('variantes/<uuid:pk>/supprimer/', views.variante_delete, name='variante_delete'),
    path('variantes/<uuid:pk>/accepter/', views.variante_accepter, name='variante_accepter'),

    # Lignes
    path('variantes/<uuid:variante_pk>/lignes/nouvelle/', views.ligne_create, name='ligne_create'),
    path('lignes/<uuid:pk>/modifier/', views.ligne_update, name='ligne_update'),
    path('lignes/<uuid:pk>/supprimer/', views.ligne_delete, name='ligne_delete'),

    # AJAX
    path('api/article/<uuid:pk>/', views.article_info, name='article_info'),

    # Dossiers FAB
    path('dossiers/', views.dossier_list, name='dossier_list'),
    path('dossiers/<uuid:pk>/', views.dossier_detail, name='dossier_detail'),
]