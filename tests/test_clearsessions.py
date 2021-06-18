from django.test import TestCase
from django.contrib.sessions.models import Session
from django.conf import settings
from django.core import management
from django_cas.models import SessionServiceTicket
from importlib import import_module
from testfixtures import LogCapture


class TestClearingSessions(TestCase):

    def setUp(self):
        SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
        self.session_keys = []
        for _ in range(10):
            session = SessionStore()
            session.create()
            self.session_keys.append(session.session_key)
            SessionServiceTicket.objects.create(
                session_key=session.session_key,
                service_ticket='ST-' + session.session_key
            )

    def tearDown(self):
        Session.objects.all().delete()
        SessionServiceTicket.objects.all().delete()

    def test_remove_service_ticket(self):
        Session.objects.filter(pk__in=self.session_keys[:5]).delete()
        management.call_command('clearcassessions')
        self.assertEqual(SessionServiceTicket.objects.all().count(), 5)

    def test_no_session_removed(self):
        management.call_command('clearcassessions')
        self.assertEqual(SessionServiceTicket.objects.all().count(), 10)

    def test_logging_informations(self):
        Session.objects.all().delete()
        with LogCapture() as l:
            management.call_command('clearcassessions')
            l.check(
                ('django_cas', 'INFO', '10 cas sessions deleted')
            )

