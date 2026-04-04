from django.urls import path
from . import views

app_name = 'facturation'

urlpatterns = [
    path('', views.facture_list, name='list'),
    path('<uuid:pk>/', views.facture_detail, name='detail'),
]