from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def tiles(request):
    # Jede Kachel kann entweder "href" (Django URL-Name) oder "href_abs" (absoluter Pfad) haben.
    tiles = [
        {"href": "inv_drafts", "title": "Rechnungs-Entwürfe", "desc": "Neueste 100 Entwürfe."},
        {"href": "plan_today",      "title": "Tagesplan (Druck)",   "desc": "Termine + Aufgaben + Teams."},
                {"href_abs": "/crm/",       "title": "CRM Start",           "desc": "Zur CRM-Startseite."},
        {"href_abs": "/admin/",     "title": "Admin",               "desc": "Django Admin-Bereich."},
        # Beispiele – später aktivieren, wenn vorhanden:
        # {"href_abs": "/crm/customers/", "title": "Kunden", "desc": "Kundenliste."},
        # {"href_abs": "/crm/ocr/inbox/", "title": "OCR-Inbox", "desc": "Eingang für Belege."},
    ]
    return render(request, "tiles/index.html", {"tiles": tiles})
