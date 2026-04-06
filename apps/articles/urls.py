from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('nouveau/', views.article_create, name='create'),
    path('<uuid:pk>/', views.article_detail, name='detail'),
    path('<uuid:pk>/modifier/', views.article_update, name='update'),
    path('<uuid:pk>/mouvement/', views.mouvement_create, name='mouvement'),
    path('<uuid:pk>/mouvements/csv/', views.mouvements_csv, name='mouvements_csv'),
    path('mouvement/<uuid:pk>/modifier/', views.mouvement_update, name='mouvement_update'),
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/nouveau/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<uuid:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
]