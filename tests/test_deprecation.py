from django.test import TestCase, override_settings
import warnings
from django_cas import admin_prefix_warning


class TestCasAdminPrefixDeprecation(TestCase):

    @override_settings(CAS_ADMIN_PREFIX='/admin')
    def test_deprecation_message(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            admin_prefix_warning()
            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertIn(
                'The `CAS_ADMIN_PREFIX` is not working and will be '
                'removed in version 1.1.5. If you want to disable CAS '
                'authentication for django admin app, you should consider '
                'the new `CAS_ADMIN_AUTH` setting',
                str(w[-1].message)
            )
