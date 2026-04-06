from django.urls import path
from . import views

app_name = 'atelier'

urlpatterns = [
    path('', views.scan_badge, name='scan_badge'),
    path('dossier/', views.scan_dossier, name='scan_dossier'),
    path('dossier/<str:numero>/taches/', views.taches, name='taches'),
    path('pointage/<uuid:pk>/valider/', views.valider, name='valider'),
]