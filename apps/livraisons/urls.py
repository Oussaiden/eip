from django.urls import path
from . import views

app_name = 'livraisons'

urlpatterns = [
    path('', views.livraison_list, name='list'),
    path('<uuid:pk>/', views.livraison_detail, name='detail'),
]