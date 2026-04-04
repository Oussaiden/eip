from django.urls import path
from . import views

app_name = 'parametres'

urlpatterns = [
    path('', views.parametres_index, name='index'),
    path('<uuid:pk>/modifier/', views.parametre_update, name='update'),
]