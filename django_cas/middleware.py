"""CAS authentication middleware"""

# from urllib import urlencode
from six.moves.urllib_parse import urlencode

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth import logout as do_logout
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import ImproperlyConfigured

try:
    from django.contrib.auth.views import login, logout
except ImportError:
    from django.contrib.auth import login, logout

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

from django_cas.exceptions import CasTicketException
from django_cas.views import login as cas_login, logout as cas_logout


__all__ = ['CASMiddleware']


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def cas_request_logout_allowed(request):
    """ Checks if the remote server is allowed to send cas logout request
    If nothing is set in the CAS_LOGOUT_REQUEST_ALLOWED parameter, all remote
    servers are allowed. Be careful !
    """
    from socket import gethostbyaddr
    remote_address = get_client_ip(request)
    if remote_address:
        try:
            remote_host = gethostbyaddr(remote_address)[0]
        except:
            return False
        allowed_hosts = settings.CAS_LOGOUT_REQUEST_ALLOWED
        return not allowed_hosts or remote_host in allowed_hosts
    return False


class CASMiddleware(MiddlewareMixin):
    """Middleware that allows CAS authentication on admin pages"""

    def _is_an_admin_view(self, view_func):
        return view_func.__module__.startswith('django.contrib.admin.')

    def process_request(self, request):
        """Checks that the authentication middleware is installed"""
        error = ("The Django CAS middleware requires authentication "
                 "middleware to be installed. Edit your MIDDLEWARE "
                 "setting to insert 'django.contrib.auth.middleware."
                 "AuthenticationMiddleware'.")
        assert hasattr(request, 'user'), error

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Forwards unauthenticated requests to the admin page to the CAS
        login URL, as well as calls to django.contrib.auth.views.login and
        logout.
        """
        if view_func in (login, cas_login) and request.POST.get(
            'logoutRequest', ''):
            if cas_request_logout_allowed(request):
                return cas_logout(request, *view_args, **view_kwargs)
            return HttpResponseForbidden()

        if view_func == login:
            return cas_login(request, *view_args, **view_kwargs)
        elif view_func == logout:
            return cas_logout(request, *view_args, **view_kwargs)

        # for all view modules except django admin. by default, we redirect to
        # cas for all admin views
        # for all other views, we treats the request with respect of views
        # configuration
        if not (self._is_an_admin_view(view_func) and settings.CAS_ADMIN_AUTH):
            return None


        if request.user.is_authenticated:
            if request.user.is_staff:
                return None
            else:
                error = ('<h1>Forbidden</h1><p>You do not have staff '
                         'privileges.</p>')
                return HttpResponseForbidden(error)
        params = urlencode({REDIRECT_FIELD_NAME: request.get_full_path()})
        return HttpResponseRedirect(
            '{}?{}'.format(reverse('django_cas:login'), params)
        )

    def process_exception(self, request, exception):
        """When we get a CasTicketException, that is probably caused by the ticket timing out.
        So logout/login and get the same page again."""
        if isinstance(exception, CasTicketException):
            do_logout(request)
            # This assumes that request.path requires authentication.
            return HttpResponseRedirect(request.path)
        else:
            return None


class ProxyMiddleware(object):

    # Middleware used to "fake" the django app that it lives at the Proxy Domain
    def process_request(self, request):
        proxy = getattr(settings, 'PROXY_DOMAIN', None)
        if not proxy:
            raise ImproperlyConfigured('To use Proxy Middleware you must set a PROXY_DOMAIN setting.')
        else:
            request.META['HTTP_HOST'] = proxy
