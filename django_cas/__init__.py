"""Django CAS 1.0/2.0 authentication backend"""

from django.conf import settings
from six import iteritems

__all__ = []

_DEFAULTS = {
    'CAS_ADMIN_AUTH': True,
    'CAS_EXTRA_LOGIN_PARAMS': None,
    'CAS_IGNORE_REFERER': False,
    'CAS_LOGOUT_COMPLETELY': True,
    'CAS_REDIRECT_URL': '/',
    'CAS_RETRY_LOGIN': False,
    'CAS_SERVER_URL': None,
    'CAS_VERSION': '3',
    'CAS_GATEWAY': False,
    'CAS_PROXY_CALLBACK': None,
    'CAS_RESPONSE_CALLBACKS': None,
    'CAS_CUSTOM_FORBIDDEN': None,
    'CAS_LOGOUT_REQUEST_ALLOWED': (),
    'CAS_USER_CREATION': True,
    'CAS_USER_CREATION_CALLBACK': None,
    'CAS_USERNAME_FORMAT': None,
}

for key, value in iteritems(_DEFAULTS):
    try:
        getattr(settings, key)
    except AttributeError:
        setattr(settings, key, value)
    # Suppress errors from DJANGO_SETTINGS_MODULE not being set
    except ImportError:
        pass
