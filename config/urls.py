# ... existing code ...
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
                path("admin/", admin.site.urls),
                path("", include("accueil.urls")),
                path("", include("accounts.urls")),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=(settings.BASE_DIR / "template" / "static"))
