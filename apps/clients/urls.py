from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    path('', views.client_list, name='list'),
    path('<uuid:pk>/', views.client_detail, name='detail'),
    path('nouveau/', views.client_create, name='create'),
    path('<uuid:pk>/modifier/', views.client_update, name='update'),
    # Contacts
    path('<uuid:client_pk>/contacts/nouveau/', views.contact_create, name='contact_create'),
    path('<uuid:client_pk>/contacts/<uuid:pk>/modifier/', views.contact_update, name='contact_update'),
    path('<uuid:client_pk>/contacts/<uuid:pk>/supprimer/', views.contact_delete, name='contact_delete'),
    # Adresses
    path('<uuid:client_pk>/adresses/nouveau/', views.adresse_create, name='adresse_create'),
    path('<uuid:client_pk>/adresses/<uuid:pk>/modifier/', views.adresse_update, name='adresse_update'),
    path('<uuid:client_pk>/adresses/<uuid:pk>/supprimer/', views.adresse_delete, name='adresse_delete'),
]