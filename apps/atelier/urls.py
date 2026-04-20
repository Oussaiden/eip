from django.urls import path
from . import views

app_name = 'atelier'

urlpatterns = [
    # Machines
    path('machines/', views.machine_list, name='machine_list'),
    path('machines/nouvelle/', views.machine_create, name='machine_create'),
    path('machines/<uuid:pk>/', views.machine_detail, name='machine_detail'),
    path('machines/<uuid:pk>/modifier/', views.machine_update, name='machine_update'),

    # Scan atelier
    path('', views.scan_badge, name='scan_badge'),
    path('dossier/', views.scan_dossier, name='scan_dossier'),
    path('dossier/<str:numero>/taches/', views.taches, name='taches'),
    path('pointage/<uuid:pk>/valider/', views.valider, name='valider'),
]
