# from urlparse import urljoin
# from urllib import urlencode, urlopen
from six.moves.urllib_parse import urlencode, urljoin
from six.moves.urllib.request import urlopen
# from six import urllib

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django_cas.exceptions import CasTicketException, CasConfigException
# Ed Crewe - add in signals to delete old tickets
from django.db.models.signals import post_save
from datetime import datetime
# Single Sign Out
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib.sessions.backends.db import SessionStore
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _


class Tgt(models.Model):
    username = models.CharField(max_length=255, unique=True)
    tgt = models.CharField(max_length=255)

    def get_proxy_ticket_for(self, service):
        """Verifies CAS 2.0+ XML-based authentication ticket.

        Returns username on success and None on failure.
        """
        if not settings.CAS_PROXY_CALLBACK:
            raise CasConfigException("No proxy callback set in settings")

        try:
            from xml.etree import ElementTree
        except ImportError:
            from elementtree import ElementTree

        params = {'pgt': self.tgt, 'targetService': service}

        url = (urljoin(settings.CAS_SERVER_URL, 'proxy') + '?' +
               urlencode(params))

        page = urlopen(url)

        try:
            response = page.read()
            tree = ElementTree.fromstring(response)
            if tree[0].tag.endswith('proxySuccess'):
                return tree[0][0].text
            else:
                raise CasTicketException("Failed to get proxy ticket")
        finally:
            page.close()


class PgtIOU(models.Model):
    """ Proxy granting ticket and IOU """
    pgtIou = models.CharField(max_length=255, unique=True)
    tgt = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now=True)


def get_tgt_for(user):
    if not settings.CAS_PROXY_CALLBACK:
        raise CasConfigException("No proxy callback set in settings")

    try:
        return Tgt.objects.get(username=user.username)
    except ObjectDoesNotExist:
        raise CasTicketException("no ticket found for user " + user.username)


def delete_old_tickets(**kwargs):
    """ Delete tickets if they are over 2 days old 
        kwargs = ['raw', 'signal', 'instance', 'sender', 'created']
    """
    sender = kwargs.get('sender', None)
    now = datetime.now()
    expire = datetime(now.year, now.month, now.day - 2)
    sender.objects.filter(created__lt=expire).delete()

post_save.connect(delete_old_tickets, sender=PgtIOU)
#post_save.connect(delete_old_tickets, sender=Tgt)

#Import CASBackend after Tgt and PgtIOU class declaration
from django_cas.backends import CASBackend

cas_backend = '{0.__module__}.{0.__name__}'.format(CASBackend)


class SessionServiceTicket(models.Model):
    """ Handles a mapping between the CAS Service Ticket and the session key
    as long as user is connected to an application that uses the CASBackend
    for authentication
    """

    service_ticket = models.CharField(_('service ticket'), max_length=255, primary_key=True)
    session_key = models.CharField(_('session key'), max_length=40)

    class Meta:
        db_table = 'django_cas_session_service_ticket'
        verbose_name = _('session service ticket')
        verbose_name_plural = _('session service tickets')

    def get_session(self):
        """ Searches the session in store and returns it """
        sst = SessionStore(session_key=self.session_key)
        sst[BACKEND_SESSION_KEY] = cas_backend
        return sst

    def __unicode__(self):
        return self.service_ticket


def _is_cas_backend(session):
    """ Checks if the auth backend is CASBackend """
    if session:
        backend = session.get(BACKEND_SESSION_KEY)
        return backend == cas_backend
    return None


@receiver(user_logged_in)
def map_service_ticket(sender, **kwargs):
    """ Creates the mapping between a session key and a service ticket after user
    logged in """
    request = kwargs['request']
    ticket = request.GET.get('ticket', '')
    if ticket and _is_cas_backend(request.session):
        session_key = request.session.session_key
        SessionServiceTicket.objects.create(service_ticket=ticket,
            session_key=session_key
        )


@receiver(user_logged_out)
def delete_service_ticket(sender, **kwargs):
    """ Deletes the mapping between session key and service ticket after user
    logged out """
    request = kwargs['request']
    session_key = request.session.session_key
    SessionServiceTicket.objects.filter(session_key=session_key).delete()
