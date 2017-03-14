from django.http import HttpRequest
from django.test import TestCase, override_settings, modify_settings
from django_cas.middleware import CASMiddleware
from django.conf import settings


class TestCASMiddleware(TestCase):

    @modify_settings(MIDDLEWARE_CLASSES={
        'remove': 'django.contrib.auth.middleware.AuthenticationMiddleware'
    })
    def test_authentication_middleware_needed(self):
        with self.assertRaises(AssertionError) as cm:
            response = self.client.get('/anonymous/')

        exception = cm.exception
        self.assertIn('Edit your MIDDLEWARE_CLASSES', str(exception))

    @override_settings(CAS_ADMIN_PREFIX='/admin')
    def test_cas_admin_deprecation(self):
        with self.assertWarns(DeprecationWarning) as cm:
            response = self.client.get('/anonymous/')

        self.assertIn('removed in version 1.1.5', str(cm.warning))
