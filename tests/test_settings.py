from django.conf import settings
from django.test import TestCase


class TestDefaultSettingsValues(TestCase):

    def test_admin_auth(self):
        self.assertTrue(settings.CAS_ADMIN_AUTH)
