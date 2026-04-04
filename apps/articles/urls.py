from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('<uuid:pk>/', views.article_detail, name='detail'),
    path('nouveau/', views.article_create, name='create'),
    path('<uuid:pk>/modifier/', views.article_update, name='update'),
]