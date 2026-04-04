from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('clients/', include('apps.clients.urls')),
    path('articles/', include('apps.articles.urls')),
    path('dossiers/', include('apps.dossiers.urls')),
    path('planning/', include('apps.planning.urls')),
    path('facturation/', include('apps.facturation.urls')),
    path('livraisons/', include('apps.livraisons.urls')),
    path('achats/', include('apps.achats.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('parametres/', include('apps.parametres.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)