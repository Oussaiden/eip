# accueil/urls.py
from django.urls import path, re_path
from . import views

app_name = "accueil"

urlpatterns = [
    path("", views.home, name="home"),
    path("accueil/", views.home, name="accueil-home"),
]