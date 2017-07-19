from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
import logging
from ...models import SessionServiceTicket


logger = logging.getLogger('django_cas')


class Command(BaseCommand):

    def handle(self, *args, **options):
        sessions = Session.objects.values_list('pk', flat=True)
        cas_tickets = SessionServiceTicket.objects.exclude(
            session_key__in=sessions
        )
        cas_sessions_to_delete = cas_tickets.count()
        cas_tickets.delete()
        logger.info('%d cas sessions deleted', cas_sessions_to_delete)
