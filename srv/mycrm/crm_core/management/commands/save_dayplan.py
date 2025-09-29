import datetime
from pathlib import Path
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from crm_core.views_planner import build_context

class Command(BaseCommand):
    help = "Speichert den Tagesplan als HTML im Dateimanager (Zeitmanagement)."

    def add_arguments(self, parser):
        parser.add_argument("--date", help="YYYY-MM-DD (Standard: heute)")

    def handle(self, *args, **opts):
        if opts.get("date"):
            try:
                day = datetime.datetime.strptime(opts["date"], "%Y-%m-%d").date()
            except ValueError:
                day = timezone.localdate()
        else:
            day = timezone.localdate()

        ctx = {"print_mode": True, **build_context(day)}
        html = render_to_string("print/plan.html", ctx)
        base = Path(getattr(settings, "FILES_ROOT", "/srv/mycrm/files"))
        target = base / "Zeitmanagement"
        target.mkdir(parents=True, exist_ok=True)
        fn = target / f"Tagesplan-{day.isoformat()}.html"
        fn.write_text(html, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Gespeichert: {fn}"))
