# accounts/urls.py
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]