from django.conf import settings
from django.test import TestCase


class TestDefaultSettingsValues(TestCase):

    def test_admin_prefix(self):
        self.assertIsNone(settings.CAS_ADMIN_PREFIX)

    def test_admin_auth(self):
        self.assertTrue(settings.CAS_ADMIN_AUTH)
