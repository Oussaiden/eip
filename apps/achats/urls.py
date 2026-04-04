from django.urls import path
from . import views

app_name = 'achats'

urlpatterns = [
    path('', views.achat_list, name='list'),
    path('<uuid:pk>/', views.achat_detail, name='detail'),
]