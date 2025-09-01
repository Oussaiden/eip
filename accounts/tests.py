from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class AuthFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        # Create both a regular user and a superuser for admin tests
        self.user = User.objects.create_user(username="jane", password="secret123")
        self.admin = User.objects.create_superuser(username="admin", email="a@a.com", password="adminpass")

    def test_login_then_logout_redirects_to_login_and_session_cleared(self):
        # Login
        resp = self.client.post(reverse("login"), {"username": "jane", "password": "secret123"})
        self.assertRedirects(resp, "/")

        # Access protected home
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

        # Logout via POST
        resp = self.client.post(reverse("logout"))
        self.assertRedirects(resp, "/login/")

        # After logout, access to home should redirect to login
        resp = self.client.get("/")
        self.assertRedirects(resp, "/login/?next=/")

    def test_admin_urls_redirect_to_site_login_when_anonymous(self):
        # Anonymous access to /admin/ should redirect to /login/?next=/admin/
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith("/login/?next=/admin/"))

        # Anonymous access to /admin/login/ should redirect to /login/ directly
        resp = self.client.get("/admin/login/?next=/admin/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/login/")

    def test_admin_access_allowed_for_authenticated_superuser(self):
        self.client.login(username="admin", password="adminpass")
        resp = self.client.get("/admin/")
        # Admin index usually 200 or 302 (to app index); ensure not redirected to site login
        self.assertNotIn("/login/", resp.url if hasattr(resp, "url") else "")
        self.assertIn(resp.status_code, [200, 302])

    def test_login_subpath_redirects_to_login(self):
        resp = self.client.get("/login/accueil")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, "/login/")
