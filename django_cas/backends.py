"""CAS authentication backend"""
import json
# from urllib import urlencode, urlopen
# from urlparse import urljoin
from six.moves.urllib_parse import urlencode, urljoin
from six.moves.urllib.request import urlopen

from django.conf import settings
from django_cas.utils import cas_callbacks
from django.contrib.auth import get_user_model


__all__ = ['CASBackend']


def _verify_cas1(ticket, service):
    """Verifies CAS 1.0 authentication ticket.

    Returns username on success and None on failure.
    """

    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'validate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        verified = page.readline().strip()
        if verified == 'yes':
            return {'username': page.readline().strip()}
        else:
            return {}
    finally:
        page.close()


def _verify_cas2(ticket, service, sufix='proxyValidate'):
    return _internal_verify_cas(ticket, service, sufix)


def _verify_cas3(ticket, service, sufix='p3/proxyValidate'):
    return _internal_verify_cas(ticket, service, sufix)


def _internal_verify_cas(ticket, service, sufix):
    """Verifies CAS 2.0 and 3.0  XML-based authentication ticket.

    Returns user_data as a dict
    """

    params = {'ticket': ticket, 'service': service, 'format': 'JSON'}
    if settings.CAS_PROXY_CALLBACK:
        params['pgtUrl'] = settings.CAS_PROXY_CALLBACK

    url = (urljoin(settings.CAS_SERVER_URL, sufix) + '?' +
           urlencode(params))

    page = urlopen(url)
    try:
        service_response = json.loads(page.read()).get('serviceResponse')

        # debug code
        # from pprint import PrettyPrinter
        # pp = PrettyPinter(indent=2)
        # pp.pprint(service_response)

        success_data = service_response.get('authenticationSuccess')

        if not success_data:
            return {}
        else:
            user_data = {'username': success_data.get('user')}
            user_attributes = success_data.get('attributes', {})
            user_data.update(user_attributes)
            if settings.CAS_RESPONSE_CALLBACKS:
                cas_callbacks(user_data.copy(), settings.CAS_RESPONSE_CALLBACKS)
            return user_data
    finally:
        page.close()


def verify_proxy_ticket(ticket, service):
    """Verifies CAS 2.0+ XML-based proxy ticket.

    Returns username on success and None on failure.
    """

    try:
        from xml.etree import ElementTree
    except ImportError:
        from elementtree import ElementTree

    params = {'ticket': ticket, 'service': service}

    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' +
           urlencode(params))

    page = urlopen(url)

    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            username = tree[0][0].text
            proxies = []
            if len(tree[0]) > 1:
                for element in tree[0][1]:
                    proxies.append(element.text)
            return {"username": username, "proxies": proxies}
        else:
            return {}
    finally:
        page.close()


_PROTOCOLS = {'1': _verify_cas1, '2': _verify_cas2, '3': _verify_cas3}

if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

_verify = _PROTOCOLS[settings.CAS_VERSION]


class CASBackend(object):
    """CAS authentication backend"""

    supports_object_permissions = False
    supports_inactive_user = False

    def authenticate(self, request, ticket, service):
        """Verifies CAS ticket and gets or create User object
            NB: Use of PT to identify proxy
        """

        user_attributes = _verify(ticket, service)
        username = user_attributes.get('username', None)
        if not username:
            return None
        if settings.CAS_USERNAME_FORMAT:
            username = settings.CAS_USERNAME_FORMAT(username)
            user_attributes['username'] = username
        user_model = get_user_model()

        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            if not settings.CAS_USER_CREATION:
                return None
            else:
                if settings.CAS_USER_CREATION_CALLBACK:
                    user = cas_callbacks(
                        [user_model, user_attributes],
                        settings.CAS_USER_CREATION_CALLBACK
                    )
                else:
                    # user will have an "unusable" password
                    user = user_model.objects.create_user(username, '')
                user.save()
        return user

    def get_user(self, user_id):
        """Retrieve the user's entry in the User model if it exists"""

        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
