from django.urls import path
from . import views

app_name = 'dossiers'

urlpatterns = [
    path('', views.dossier_list, name='list'),
    path('<uuid:pk>/', views.dossier_detail, name='detail'),
    path('nouveau/', views.dossier_create, name='create'),
    path('<uuid:pk>/modifier/', views.dossier_update, name='update'),
]