from django.conf import settings
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, override_settings, modify_settings
from django.http import HttpRequest, HttpResponseRedirect
from django_cas.middleware import CASMiddleware

from .views import test_anonymous_view, test_authenticated_view


class TestCASMiddleware(TestCase):

    def test_is_an_admin_view(self):
        middleware = CASMiddleware()
        self.assertTrue(
            middleware._is_an_admin_view(AdminSite.index)
        )

    def test_is_a_normal_view(self):
        middleware = CASMiddleware()
        self.assertFalse(
            middleware._is_an_admin_view(test_anonymous_view)
        )


    @modify_settings(MIDDLEWARE={
        'remove': 'django.contrib.auth.middleware.AuthenticationMiddleware'
    })
    def test_authentication_middleware_needed(self):
        with self.assertRaises(AssertionError) as cm:
            response = self.client.get('/anonymous/')

        exception = cm.exception
        self.assertIn('Edit your MIDDLEWARE', str(exception))

    def test_normal_view(self):
        middleware = CASMiddleware()
        request = HttpRequest()
        response = middleware.process_view(request, test_anonymous_view, (), {})
        self.assertIsNone(response)

    @override_settings(CAS_ADMIN_AUTH=False)
    def test_normal_view_with_admin_cas_disabled(self):
        middleware = CASMiddleware()
        request = HttpRequest()
        response = middleware.process_view(request, test_anonymous_view, (), {})
        self.assertIsNone(response)

    def test_admin_view(self):
        middleware = CASMiddleware()
        request = HttpRequest()
        request.user = AnonymousUser()
        response = middleware.process_view(request, AdminSite.index, (), {})
        self.assertIsInstance(response, HttpResponseRedirect)

    @override_settings(CAS_ADMIN_AUTH=False)
    def test_admin_view_with_admin_cas_disabled(self):
        middleware = CASMiddleware()
        request = HttpRequest()
        response = middleware.process_view(request, AdminSite.index, (), {})
        self.assertIsNone(response)
