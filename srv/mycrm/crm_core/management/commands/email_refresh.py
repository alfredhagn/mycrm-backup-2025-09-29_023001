from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.urls import reverse
from django.conf import settings


class Command(BaseCommand):
    help = "Trigger E-Mail-Refresh, indem die View 'crm_core:email_refresh' als ein Benutzer aufgerufen wird."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-id",
            type=int,
            help="User-ID, unter der der Refresh ausgeführt werden soll (Standard: erster Superuser oder Staff).",
        )

    def handle(self, *args, **opts):
        # 'testserver' für RequestFactory erlauben
        if "testserver" not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = list(settings.ALLOWED_HOSTS) + ["testserver"]

        # Benutzer auswählen
        User = get_user_model()
        user = None
        uid = opts.get("user_id")
        if uid:
            user = User.objects.filter(id=uid).first()
            if not user:
                raise CommandError(f"Benutzer mit id={uid} nicht gefunden.")
        if not user:
            user = User.objects.filter(is_superuser=True).first() or User.objects.filter(is_staff=True).first()
        if not user:
            raise CommandError("Kein geeigneter Benutzer gefunden (Superuser/Staff). Bitte --user-id angeben.")

        # View laden
        try:
            from crm_core import views as crm_views
            view = getattr(crm_views, "email_refresh")
        except Exception as e:
            raise CommandError(f"View crm_core.views.email_refresh nicht gefunden: {e}")

        # Fake-Request bauen (Session + Messages + User)
        rf = RequestFactory()
        path = reverse("crm_core:email_refresh")
        req = rf.get(path)

        # Session
        SessionMiddleware(lambda r: None).process_request(req)
        req.session.save()

        # Auth & Messages
        req.user = user
        setattr(req, "_messages", FallbackStorage(req))

        # Aufruf
        resp = view(req)
        status = getattr(resp, "status_code", None)
        if status is None or not (200 <= status < 400):
            raise CommandError(f"email_refresh lieferte HTTP {status}")
        self.stdout.write(self.style.SUCCESS(f"email_refresh OK (HTTP {status}) als {user}"))
