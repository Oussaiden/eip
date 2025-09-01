from django.http import HttpResponseRedirect
from django.urls import reverse


class AdminLoginRedirectMiddleware:
    """
    Redirect unauthenticated users away from Django admin login page to the site login.
    - /admin/login/ (any query) -> /login/
    - Other /admin/* when not authenticated -> /login/?next=<requested path>
    Authenticated users proceed normally.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        path = request.path

        if user is None or not user.is_authenticated:
            if path.startswith("/admin/"):
                # If specifically the admin login page, do not show it; redirect to site login without next
                if path.startswith("/admin/login"):
                    return HttpResponseRedirect(reverse("login"))
                # For other admin URLs, preserve intent via next parameter
                login_url = reverse("login")
                return HttpResponseRedirect(f"{login_url}?next={path}")

        return self.get_response(request)
