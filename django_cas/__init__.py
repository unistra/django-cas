"""Django CAS 1.0/2.0 authentication backend"""

from django.conf import settings
from six import iteritems

__all__ = []

_DEFAULTS = {
    'CAS_ADMIN_PREFIX': None,
    'CAS_ADMIN_AUTH': True,
    'CAS_EXTRA_LOGIN_PARAMS': None,
    'CAS_IGNORE_REFERER': False,
    'CAS_LOGOUT_COMPLETELY': True,
    'CAS_REDIRECT_URL': '/',
    'CAS_RETRY_LOGIN': False,
    'CAS_SERVER_URL': None,
    'CAS_VERSION': '2',
    'CAS_GATEWAY': False,
    'CAS_PROXY_CALLBACK': None,
    'CAS_RESPONSE_CALLBACKS': None,
    'CAS_CUSTOM_FORBIDDEN':None,
    'CAS_LOGOUT_REQUEST_ALLOWED': (),
    'CAS_USER_CREATION': True,
    'CAS_USERNAME_FORMAT': None
}

for key, value in iteritems(_DEFAULTS):
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    # Suppress errors from DJANGO_SETTINGS_MODULE not being set
    except ImportError:
        pass


def admin_prefix_warning():
    if getattr(settings, 'CAS_ADMIN_PREFIX', None) is not None:
        import warnings
        warnings.warn(
            'The `CAS_ADMIN_PREFIX` is not working and will be '
            'removed in version 1.1.5. If you want to disable CAS '
            'authentication for django admin app, you should consider '
            'the new `CAS_ADMIN_AUTH` setting',
            DeprecationWarning
        )
