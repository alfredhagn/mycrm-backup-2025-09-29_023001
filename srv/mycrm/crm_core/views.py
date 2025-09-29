import base64
import os
from dotenv import load_dotenv

from urllib3.exceptions import InsecureRequestWarning
import urllib3
if os.getenv("FRITZBOX_VERIFY_TLS","true").strip().lower() in ("0","false","no"):
    urllib3.disable_warnings(InsecureRequestWarning)

load_dotenv(os.getenv("MYCRM_ENV_FILE", "/etc/mycrm.env"))

from urllib3.exceptions import InsecureRequestWarning
import urllib3
if os.getenv("FRITZBOX_VERIFY_TLS","true").strip().lower() in ("0","false","no"):
    urllib3.disable_warnings(InsecureRequestWarning)


from datetime import timezone as dt_timezone

from django.http import HttpResponse
from django.conf import settings
from django.contrib import messages
import json
import logging
import requests
from typing import Dict, Any, Optional
import logging
import requests
from typing import Dict, Any, Optional
from typing import Dict, Optional
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone as dj_tz
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Company, Contact, FileAsset  # EmailLog optional via _import_emaillog_model(), 
from .forms import CompanyForm, ContactForm 
from django.template.loader import select_template
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET


from django.http import JsonResponse
from .ms_tokens import get_ms_session

def my_inbox_preview(request):
    s = get_ms_session(request.user)
    resp = s.get("https://graph.microsoft.com/v1.0/me/messages?$top=5")
    resp.raise_for_status()
    return JsonResponse(resp.json())





LOGGER = logging.getLogger(__name__)

def render_first(request, candidates, context=None):
    """
    Rendert das erste existierende Template aus 'candidates' mit 'context'.
    """
    tpl = select_template(candidates)
    return HttpResponse(tpl.render(context or {}, request))


# ---------------------------------------------------------------------
# Microsoft Graph Basics
# ---------------------------------------------------------------------
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _graph_headers(token: str) -> Dict[str, str]:
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _graph_url(path: str) -> str:
    return f"{GRAPH_BASE}{path if path.startswith('/') else '/' + path}"


def _graph_get(token: str, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
    return requests.get(_graph_url(path), headers=_graph_headers(token), params=params, timeout=30)


def _graph_post(token: str, path: str, payload: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> requests.Response:
    headers = {**_graph_headers(token), "Content-Type": "application/json"}
    return requests.post(_graph_url(path), headers=headers, data=json.dumps(payload), params=params, timeout=30)


def _graph_patch(token: str, path: str, payload: Dict[str, Any]) -> requests.Response:
    headers = {**_graph_headers(token), "Content-Type": "application/json"}
    return requests.patch(_graph_url(path), headers=headers, data=json.dumps(payload), timeout=30)


def _graph_delete(token: str, path: str) -> requests.Response:
    return requests.delete(_graph_url(path), headers=_graph_headers(token), timeout=30)


# ---------------------------------------------------------------------
# TZ- und Datums-Helfer
# ---------------------------------------------------------------------
def _ensure_aware(dt):
    return dj_tz.make_aware(dt, dj_tz.get_current_timezone()) if dj_tz.is_naive(dt) else dt


def _utc_iso(dt=None) -> str:
    if dt is None:
        dt = dj_tz.now()
    return _ensure_aware(dt).astimezone(dt_timezone.utc).isoformat()


def _dt_to_str(graph_dt: Dict[str, str]) -> str:
    """
    MS Graph {"dateTime": "...", "timeZone": "..."} -> lokale, hübsche Zeit.
    """
    try:
        from dateutil import parser
        dt = parser.isoparse(graph_dt.get("dateTime"))
        return dt.astimezone(timezone.get_current_timezone()).strftime("%d.%m.%Y %H:%M")
    except Exception:
        return graph_dt.get("dateTime") or ""


# ---------------------------------------------------------------------
# Optionale Modelle/Formulare
# ---------------------------------------------------------------------
def _import_emaillog_model():
    try:
        from .models import EmailLog  # type: ignore
        return EmailLog
    except Exception:
        return None


def dashboard(request):
    """
    Einfaches CRM-Dashboard / Startseite
    """
    return render(request, "crm_core/dashboard.html", {})



    return render(request, "email/home.html")



@require_GET
def email_home(request):
    return render(request, "email/home.html")

@require_http_methods(["POST"])
def email_reply_all(request, message_id: str):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:inbox")

    comment = request.POST.get("comment", "")
    payload = {"comment": comment}

    r = _graph_post(token, f"/me/messages/{message_id}/createReplyAll", payload={})
    if r.status_code not in (200, 201, 202):
        messages.error(request, f"Antwort an alle konnte nicht erstellt werden ({r.status_code})")
        return redirect("crm_core:inbox")

    reply_id = r.json().get("id")
    if reply_id:
        send_r = _graph_post(token, f"/me/messages/{reply_id}/send", payload={})
        if send_r.status_code in (200, 202):
            messages.success(request, "Antwort an alle wurde gesendet.")
        else:
            messages.warning(request, "Antwort an alle wurde erstellt, aber nicht gesendet.")
    else:
        messages.error(request, "Antwort-ID fehlt.")

    return redirect("crm_core:inbox")

@require_http_methods(["POST"])
def email_forward(request, message_id: str):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:inbox")

    comment = request.POST.get("comment", "")
    to_recipients = request.POST.get("to", "").split(",")

    payload = {
        "comment": comment,
        "toRecipients": [{"emailAddress": {"address": email.strip()}} for email in to_recipients if email.strip()]
    }

    r = _graph_post(token, f"/me/messages/{message_id}/forward", payload)
    if r.status_code in (200, 202):
        messages.success(request, "E-Mail wurde weitergeleitet.")
    else:
        messages.error(request, f"Weiterleitung fehlgeschlagen ({r.status_code})")

    return redirect("crm_core:inbox")


@require_GET
def microsoft_auth_init(request):
    # leitet zum allauth Microsoft Login
    return redirect("/accounts/microsoft/login/")

@require_GET
def microsoft_auth_callback(request):
    # Platzhalter – nach erfolgreichem Login zurück ins Dashboard
    messages.success(request, "Microsoft Login Callback erreicht (Platzhalter).")
    return redirect("crm_core:dashboard")

@require_GET
def company_list(request):
    companies = Company.objects.all().order_by("name")
    return render(request, "crm_core/company_list.html", {"companies": companies})

@require_GET
def company_detail(request, pk: int):
    company = get_object_or_404(Company, pk=pk)
    return render(request, "crm_core/company_detail.html", {"company": company})

@require_http_methods(["GET", "POST"])
def company_create(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, "Firma wurde erstellt.")
            return redirect("crm_core:company_detail", pk=company.pk)
    else:
        form = CompanyForm()
    return render(request, "crm_core/company_form.html", {"form": form})

@require_http_methods(["GET", "POST"])
def company_update(request, pk: int):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "POST":
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "Firma wurde aktualisiert.")
            return redirect("crm_core:company_detail", pk=company.pk)
    else:
        form = CompanyForm(instance=company)
    return render(request, "crm_core/company_form.html", {"form": form, "company": company})


@require_http_methods(["GET", "POST"])
def company_delete(request, pk: int):
    company = get_object_or_404(Company, pk=pk)
    if request.method == "GET":
        return render(request, "crm_core/companies/delete_confirm.html", {"company": company})
    company.delete()
    messages.success(request, "Firma wurde gelöscht.")
    return redirect("crm_core:company_list")

@require_GET
def contact_list(request):
    contacts = Contact.objects.all().order_by("last_name", "first_name")
    return render(request, "crm_core/contact_list.html", {"contacts": contacts})

@require_GET
def contact_detail(request, pk: int):
    contact = get_object_or_404(Contact, pk=pk)
    logs = CallLog.objects.filter(contact=contact).order_by("-started_at")[:20]
    return render(request, "crm_core/contact_detail.html", {"contact": contact, "call_logs": logs})

@require_http_methods(["GET", "POST"])
def contact_create(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, "Kontakt wurde erstellt.")
            return redirect("crm_core:contact_detail", pk=contact.pk)
    else:
        form = ContactForm()
    return render(request, "crm_core/contact_form.html", {"form": form})

@require_http_methods(["GET", "POST"])
def contact_update(request, pk: int):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            messages.success(request, "Kontakt wurde aktualisiert.")
            return redirect("crm_core:contact_detail", pk=contact.pk)
    else:
        form = ContactForm(instance=contact)
    return render(request, "crm_core/contact_form.html", {"form": form, "contact": contact})

@require_http_methods(["GET", "POST"])
def contact_delete(request, pk: int):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "GET":
        return render(request, "crm_core/contacts/delete_confirm.html", {"contact": contact})
    contact.delete()
    messages.success(request, "Kontakt wurde gelöscht.")
    return redirect("crm_core:contact_list")


@require_GET
def inbox_view(request):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    r = _graph_get(token, "/me/mailFolders/inbox/messages", params={"$top": 25, "$orderby": "receivedDateTime DESC"})
    print("📥 Statuscode:", r.status_code)
    print("📥 Antwort:", r.text[:500])
    if r.status_code == 200 and not r.json().get("value"):
        messages.warning(request, "⚠️ Keine E-Mails gefunden (API-Antwort leer?)")
    items = r.json().get("value", []) if r.status_code == 200 else []
    return render(request, "email/inbox.html", {"emails": items})

@require_GET
def sent_view(request):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    r = _graph_get(token, "/me/mailFolders/sentitems/messages", params={"$top": 25, "$orderby": "receivedDateTime DESC"})
    items = r.json().get("value", []) if r.status_code == 200 else []
    return render(request, "email/sent.html", {"emails": items})

@require_GET
def email_refresh(request):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    # Nur Dummy – tatsächliche Sync-Logik kann später ergänzt werden
    messages.success(request, "E-Mail-Liste wurde aktualisiert.")
    return redirect("crm_core:inbox")

@require_GET
def email_detail(request, message_id: str):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    r = _graph_get(token, f"/me/messages/{message_id}")
    if r.status_code != 200:
        messages.error(request, f"E-Mail konnte nicht geladen werden ({r.status_code})")
        return redirect("crm_core:inbox")

    msg = r.json()
    attachments = []
    att_r = _graph_get(token, f"/me/messages/{message_id}/attachments")
    if att_r.status_code == 200:
        attachments = att_r.json().get("value", [])

    return render(
        request,
        "crm_core/email_detail.html",
        {"message": msg, "attachments": attachments, "message_id": message_id},
    )

@require_POST
def email_delete(request, message_id: str):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    r = _graph_delete(token, f"/me/messages/{message_id}")
    if r.status_code in (200, 204):
        messages.success(request, "E-Mail gelöscht.")
    else:
        messages.error(request, f"E-Mail konnte nicht gelöscht werden ({r.status_code}).")
    return redirect("crm_core:inbox")

@require_GET
def email_attachment_download(request, message_id: str, attachment_id: str):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    r = _graph_get(token, f"/me/messages/{message_id}/attachments/{attachment_id}")
    if r.status_code != 200:
        messages.error(request, "Anhang konnte nicht heruntergeladen werden.")
        return redirect("crm_core:email_detail", message_id=message_id)

    att = r.json()
    content = att.get("contentBytes")
    filename = att.get("name", "attachment")

    import base64
    from django.http import HttpResponse

    if content:
        data = base64.b64decode(content)
        response = HttpResponse(data, content_type="application/octet-stream")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    messages.error(request, "Anhang war leer.")
    return redirect("crm_core:email_detail", message_id=message_id)

@require_GET
def email_inbox(request):
    # historischer Alias -> leitet auf die neue Inbox-Ansicht weiter
    return inbox_view(request)

@require_GET
def email_attachments(request, message_id: str):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    r = _graph_get(token, f"/me/messages/{message_id}/attachments")
    if r.status_code == 200:
        attachments = r.json().get("value", [])
    else:
        attachments = []
        messages.error(request, "Anhänge konnten nicht geladen werden.")

    return render(request, "email/attachments.html", {
        "attachments": attachments,
        "message_id": message_id,
    })

@require_http_methods(["GET", "POST"])
def contact_create_from_email(request):
    """
    Erstellt einen neuen Kontakt basierend auf Maildaten.
    Erwartet: request.GET["name"], request.GET["email"]
    """
    initial_data = {}
    if "name" in request.GET:
        initial_data["first_name"] = request.GET["name"]
    if "email" in request.GET:
        initial_data["email"] = request.GET["email"]

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, "Kontakt aus E-Mail erstellt.")
            return redirect("crm_core:contact_detail", pk=contact.pk)
    else:
        form = ContactForm(initial=initial_data)

    return render(request, "crm_core/contact_form.html", {"form": form})

@require_GET
def email_log_list(request):
    # Beispielhafte Logs – später durch DB/Graph-Daten ersetzen
    logs = [
        {"timestamp": "2025-08-18 21:00", "status": "Gesendet",     "recipient": "a@example.com"},
        {"timestamp": "2025-08-18 21:15", "status": "Fehlgeschlagen","recipient": "b@example.com"},
    ]
    return render(request, "email/logs.html", {"logs": logs})

# --- File Manager (echte Dateien im MEDIA_ROOT) -----------------------
import os
from pathlib import Path
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET, require_http_methods, require_POST


def _media_root() -> Path:
    root = getattr(settings, "MEDIA_ROOT", None)
    if not root:
        # Fallback: ./media relativ zum Projekt (nur wenn MEDIA_ROOT nicht gesetzt)
        root = Path(__file__).resolve().parent.parent.parent / "media"
    return Path(root).resolve()


def _safe_media_path(filename: str) -> Path:
    """
    Verhindert Path-Traversal; erlaubt nur Pfade unterhalb MEDIA_ROOT.
    """
    base = _media_root()
    target = (base / filename).resolve()
    if not str(target).startswith(str(base)):
        # z.B. "../../etc/passwd"
        raise Http404("Ungültiger Dateipfad.")
    return target


def _human_size(num: int) -> str:
    for unit in ["Bytes", "KB", "MB", "GB", "TB"]:
        if num < 1024.0 or unit == "TB":
            return f"{num:.0f} {unit}" if unit == "Bytes" else f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


@require_GET
def files_list(request):
    base = _media_root()
    if not base.exists():
        base.mkdir(parents=True, exist_ok=True)

    items = []
    for p in sorted(base.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_file():
            continue
        stat = p.stat()
        items.append({
            "name": p.name,
            "size": _human_size(stat.st_size),
            "uploaded": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        })

    rel = request.GET.get("p", "").strip()
    return render(request, "files/list.html", {"rel": rel, "files": items})


@require_http_methods(["GET", "POST"])
def files_upload(request):
    base = _media_root()
    base.mkdir(parents=True, exist_ok=True)

    if request.method == "GET":
        return render(request, "files/upload.html")

    # POST
    f = request.FILES.get("file")
    if not f:
        messages.error(request, "Keine Datei ausgewählt.")
        return redirect("crm_core:files_upload")

    # Kollisionen vermeiden: vorhandene Dateien nummerieren
    dest = base / f.name
    if dest.exists():
        stem = dest.stem
        suffix = dest.suffix
        i = 1
        while True:
            candidate = base / f"{stem}_{i}{suffix}"
            if not candidate.exists():
                dest = candidate
                break
            i += 1

    with dest.open("wb+") as out:
        for chunk in f.chunks():
            out.write(chunk)

    messages.success(request, f"Datei {dest.name} erfolgreich hochgeladen.")
    return redirect("crm_core:files_list")


@require_GET
def files_download(request, filename: str):
    try:
        path = _safe_media_path(filename)
    except Http404:
        messages.error(request, "Ungültiger Dateiname.")
        return redirect("crm_core:files_list")

    if not path.exists() or not path.is_file():
        messages.error(request, "Datei nicht gefunden.")
        return redirect("crm_core:files_list")

    return FileResponse(open(path, "rb"), as_attachment=True, filename=path.name)


@require_POST
def files_delete(request, filename: str):
    try:
        path = _safe_media_path(filename)
    except Http404:
        messages.error(request, "Ungültiger Dateiname.")
        return redirect("crm_core:files_list")

    if path.exists() and path.is_file():
        try:
            path.unlink()
            messages.success(request, f"{path.name} wurde gelöscht.")
        except Exception as e:
            messages.error(request, f"Datei konnte nicht gelöscht werden: {e}")
    else:
        messages.warning(request, "Datei war nicht mehr vorhanden.")
    return redirect("crm_core:files_list")



# --- Fritzbox Calllist (CSV, robust mit Fallbacks) -------------------
import os
import csv
import requests
from requests.auth import HTTPBasicAuth
from django.views.decorators.http import require_GET
from django.contrib import messages
from django.shortcuts import render

def _fritz_env():
    host = os.getenv("FRITZBOX_HOST", "fritz.box").strip()
    scheme = os.getenv("FRITZBOX_SCHEME", "http").strip().lower()  # "http" oder "https"
    verify_env = os.getenv("FRITZBOX_VERIFY_TLS", "true").strip().lower()
    verify = verify_env in ("1", "true", "yes")
    user = os.getenv("FRITZBOX_USERNAME", "").strip()
    pwd  = os.getenv("FRITZBOX_PASSWORD", "").strip()
    base = f"{scheme}://{host}"
    return base, user, pwd, verify

def _fritz_parse_csv(text: str):
    if isinstance(text, bytes):
        try:
            text = text.decode("iso-8859-1", errors="ignore")
        except Exception:
            text = text.decode("utf-8", errors="ignore")
    if not text:
        return []

    lines = text.replace("\r\n", "\n").splitlines()
    if lines and lines[0].strip().lower().startswith('sep='):
         lines = lines[1:]
    if lines and lines[0].strip().lower().startswith('sep='):
         lines = lines[1:]
    if not lines:
        return []

    reader = csv.reader(lines, delimiter=';')
    rows = list(reader)
    if not rows:
        return []

    header = [h.strip().lower() for h in rows[0]]
    data = rows[1:]

    def idx(*cands):
        for c in cands:
            try:
                return header.index(c)
            except ValueError:
                continue
        return None




# ---------------------------------------------------------------------
# MS Graph Token holen – robust
# ---------------------------------------------------------------------

@require_GET
def token_debug(request):
    token = _require_token(request)
    if token:
        return HttpResponse(f"Token gefunden: {token[:50]}...")
    return HttpResponse("❌ Kein gültiger Microsoft-Token.")


def _require_token(request):
    """
    Holt einen gültigen Microsoft OAuth Token aus Session oder allauth.
    """
    from allauth.socialaccount.models import SocialToken

    # Debug-Ausgabe
    print("🟢 Benutzer:", request.user)
    print("🟢 Authentifiziert:", request.user.is_authenticated)

def _fritz_get_sid(base: str, user: str, pwd: str, verify: bool, timeout: int = 10) -> str | None:

    """

    Versucht, via login_sid.lua eine SID zu bekommen.

    Einfacher Pfad: POST username/password (ab neueren FritzOS-Versionen möglich).

    """

    try:

        requests.get(f"{base}/login_sid.lua", timeout=timeout, verify=verify)

        r = requests.post(

            f"{base}/login_sid.lua",

            data={"username": user, "password": pwd},

            timeout=timeout,

            verify=verify,

        )

        if r.status_code != 200:

            return None

        text = r.text

        start = text.find("<SID>")

        end = text.find("</SID>")

        if start != -1 and end != -1:

            sid = text[start+5:end].strip()

            if sid and sid != "0000000000000000":

                return sid

    except Exception:

        return None

    return None

    if request.method == "POST":
        to = request.POST.get("to", "")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")
        cc = request.POST.get("cc", "")
        bcc = request.POST.get("bcc", "")

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in to.split(",") if addr.strip()],
                "ccRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in cc.split(",") if addr.strip()],
                "bccRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in bcc.split(",") if addr.strip()],
            },
            "saveToSentItems": "true"
        }

        r = _graph_post(token, "/me/sendMail", payload=message)
        if r.status_code == 202:
            messages.success(request, "E-Mail gesendet.")
            return redirect("crm_core:sent")
        else:
            messages.error(request, f"Senden fehlgeschlagen ({r.status_code}).")

        # Bei Fehler neu befüllen
        prefill.update({"to": to, "cc": cc, "bcc": bcc, "subject": subject, "body": body})

    return render(request, "email/send.html", {"prefill": prefill})


# Kalender
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotAllowed

@require_GET
def calendar_detail(request, event_id):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:calendar_list")

    r = _graph_get(token, f"/me/events/{event_id}")
    if r.status_code != 200:
        messages.error(request, "Termin nicht gefunden.")
        return redirect("crm_core:calendar_list")

    event = r.json()
    return render(request, "calendar/detail.html", {"event": event})


@require_http_methods(["GET", "POST"])
def calendar_edit(request, event_id):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:calendar_list")

    if request.method == "GET":
        r = _graph_get(token, f"/me/events/{event_id}")
        if r.status_code != 200:
            messages.error(request, "Termin nicht gefunden.")
            return redirect("crm_core:calendar_list")

        event = r.json()
        return render(request, "calendar/edit.html", {"event": event})

    # POST – Daten speichern
    subject = request.POST.get("subject")
    body = request.POST.get("body")
    start = request.POST.get("start")
    end = request.POST.get("end")

    payload = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body,
        },
        "start": {
            "dateTime": start,
            "timeZone": "Europe/Vienna",
        },
        "end": {
            "dateTime": end,
            "timeZone": "Europe/Vienna",
        },
    }

    r = _graph_patch(token, f"/me/events/{event_id}", payload=payload)
    if r.status_code == 200:
        messages.success(request, "Termin aktualisiert.")
    else:
        messages.error(request, "Änderung fehlgeschlagen.")

    return redirect("crm_core:calendar_list")


@require_http_methods(["GET", "POST"])
def calendar_delete(request, event_id):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:calendar_list")

    if request.method == "GET":
        # Abruf zum Anzeigen des Lösch-Dialogs
        r = _graph_get(token, f"/me/events/{event_id}")
        if r.status_code != 200:
            messages.error(request, "Termin nicht gefunden.")
            return redirect("crm_core:calendar_list")

        event = r.json()
        return render(request, "calendar/delete_confirm.html", {"event": event})

    # POST – Löschen bestätigen
    r = _graph_delete(token, f"/me/events/{event_id}")
    if r.status_code == 204:
        messages.success(request, "Termin gelöscht.")
    else:
        messages.error(request, "Löschen fehlgeschlagen.")

    return redirect("crm_core:calendar_list")

@require_GET
def calendar_list(request):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:home")

    # Abruf der Kalendertermine über Microsoft Graph API
    r = _graph_get(token, "/me/events?$orderby=start/dateTime desc")

    if r.status_code != 200:
        messages.error(request, "Fehler beim Laden der Termine.")
        return redirect("crm_core:home")

    events = r.json().get("value", [])
    events_disp = []
    for _e in events:
        sd = _dt_to_str((_e.get("start") or {}))
        ed = _dt_to_str((_e.get("end") or {}))
        loc = (_e.get("location") or {}).get("displayName")
        _e["start_display"] = sd
        _e["end_display"]  = ed
        _e["location_display"] = loc
        _e["is_all_day_display"] = "Ja" if _e.get("isAllDay") else "Nein"
        events_disp.append(_e)
    return render(request, "crm_core/calendar/index.html", {"events": events_disp})

@require_http_methods(["GET", "POST"])
def calendar_create(request):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:calendar_list")

    if request.method == "GET":
        return render(request, "calendar/create.html")

    # POST – Termin anlegen
    subject = request.POST.get("subject")
    body = request.POST.get("body")
    start = request.POST.get("start")
    end = request.POST.get("end")

    event = {
        "subject": subject,
        "body": {
            "contentType": "Text",
            "content": body
        },
        "start": {
            "dateTime": start,
            "timeZone": "Europe/Vienna"
        },
        "end": {
            "dateTime": end,
            "timeZone": "Europe/Vienna"
        }
    }

    r = _graph_post(token, "/me/events", payload=event)
    if r.status_code == 201:
        messages.success(request, "Termin erfolgreich erstellt.")
        return redirect("crm_core:calendar_list")
    else:
        messages.error(request, "Erstellen fehlgeschlagen.")
        return render(request, "calendar/create.html", {"prefill": request.POST})

import os, requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_POST
def call_number_via_sipgate(request):
    number = request.POST.get("number")
    if not number:
        return JsonResponse({"error": "Nummer fehlt"}, status=400)

    token_id = os.getenv("SIPGATE_TOKEN_ID")
    token = os.getenv("SIPGATE_TOKEN")

    url = "https://api.sipgate.com/v2/sessions/calls"
    data = {
        "deviceId": "e0",  # ggf. anpassen
        "caller": "492211234567",  # deine eigene Rufnummer
        "callee": number
    }
    resp = requests.post(url, json=data, auth=(token_id, token))

    if resp.status_code == 201:
        return JsonResponse({"success": True, "message": f"Call to {number} initiated"})
    else:
        return JsonResponse({"error": resp.text}, status=resp.status_code)


# --- Saubere Definition von _try_fetch_csv (neu) -------------------
def _try_fetch_csv(base: str, user: str, pwd: str, verify: bool) -> tuple[list[dict], str | None]:
    """
    Probiert beide CSV-Pfade:
      1) /calllist.lua?csv=
      2) /fon_num/foncalls_list.lua?csv=
    Erst mit Basic-Auth, dann (falls nötig) mit SID.
    """
    paths = ["/calllist.lua", "/fon_num/foncalls_list.lua"]
    timeout = 10

    # A) Direkt mit Basic-Auth probieren
    for rel in paths:
        url = f"{base}{rel}?csv=&max=1000"
        try:
            r = requests.get(url, auth=HTTPBasicAuth(user, pwd), timeout=timeout, verify=verify)
            if r.status_code == 200 and r.content:
                items = _fritz_parse_csv(r.content)
                if items:
                    return items, url
        except Exception:
            pass

    # B) Mit SID probieren
    sid = _fritz_get_sid(base, user, pwd, verify)
    if sid:
        for rel in paths:
            url = f"{base}{rel}?csv=&max=1000&sid={sid}"
            try:
                r = requests.get(url, timeout=timeout, verify=verify)
                if r.status_code == 200 and r.content:
                    items = _fritz_parse_csv(r.content)
                    if items:
                        return items, url
            except Exception:
                pass

    return [], None

@require_http_methods(["GET", "POST"])
def email_compose(request):
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_home")

    prefill = {
        "to": request.GET.get("to", ""),
        "cc": request.GET.get("cc", ""),
        "bcc": request.GET.get("bcc", ""),
        "subject": request.GET.get("subject", ""),
        "body": request.GET.get("body", ""),
    }

    if request.method == "POST":
        to = request.POST.get("to", "")
        cc = request.POST.get("cc", "")
        bcc = request.POST.get("bcc", "")
        subject = request.POST.get("subject", "")
        body = request.POST.get("body", "")

        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in to.split(",") if addr.strip()],
                "ccRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in cc.split(",") if addr.strip()],
                "bccRecipients": [{"emailAddress": {"address": addr.strip()}} for addr in bcc.split(",") if addr.strip()],
            },
            "saveToSentItems": "true"
        }

        r = _graph_post(token, "/me/sendMail", payload=message)
        if r.status_code == 202:
            messages.success(request, "E-Mail gesendet.")
            return redirect("crm_core:sent")
        else:
            messages.error(request, f"Senden fehlgeschlagen ({r.status_code}).")

        prefill.update({"to": to, "cc": cc, "bcc": bcc, "subject": subject, "body": body})

    return render(request, "email/send.html", {"prefill": prefill})

@require_GET
def fritzbox_call_list(request):
    base, user, pwd, verify = _fritz_env()

    if not user or not pwd:
        messages.error(request, "Fritzbox-Zugangsdaten fehlen (FRITZBOX_USERNAME / FRITZBOX_PASSWORD).")
        return render(request, "crm_core/voip/call_list.html", {"calls": []})

    calls, used_url = _try_fetch_csv(base, user, pwd, verify)

    if not calls:
        messages.error(
            request,
            "Anrufliste konnte nicht geladen werden (404/401/leer). Prüfe Pfad, Login und Rechte der Fritzbox."
        )
    else:
        messages.success(request, f"Anrufliste geladen ({len(calls)} Einträge).")

    return render(request, "crm_core/voip/call_list.html", {"calls": calls})

# --- Fritz!Box: SID via Challenge-Response (robust) -----------------
def _fritz_get_sid(base: str, user: str, pwd: str, verify: bool, timeout: int = 10) -> str | None:
    """
    Holt eine gültige SID von der Fritz!Box via login_sid.lua (Challenge-Response).
    Versucht zuerst Plain-POST (falls Firmware es noch erlaubt), sonst Challenge-Response.
    """
    try:
        # A) Evtl. akzeptiert die Box noch Plain-POST
        try:
            r = requests.post(f"{base}/login_sid.lua",
                              data={"username": user, "password": pwd},
                              timeout=timeout, verify=verify)
            if r.status_code == 200:
                txt = r.text
                s = txt.find("<SID>"); e = txt.find("</SID>")
                if s != -1 and e != -1:
                    sid = txt[s+5:e].strip()
                    if sid and sid != "0000000000000000":
                        return sid
        except Exception:
            pass

        # B) Challenge-Response
        r0 = requests.get(f"{base}/login_sid.lua", timeout=timeout, verify=verify)
        if r0.status_code != 200:
            return None
        t0 = r0.text
        sC = t0.find("<Challenge>"); eC = t0.find("</Challenge>")
        if sC == -1 or eC == -1:
            return None
        challenge = t0[sC+11:eC].strip()

        import hashlib
        payload = (challenge + "-" + pwd).encode("utf-16le")
        response = f"{challenge}-{hashlib.md5(payload).hexdigest()}"

        r1 = requests.get(f"{base}/login_sid.lua",
                          params={"username": user, "response": response},
                          timeout=timeout, verify=verify)
        if r1.status_code != 200:
            return None
        t1 = r1.text
        sS = t1.find("<SID>"); eS = t1.find("</SID>")
        if sS != -1 and eS != -1:
            sid = t1[sS+5:eS].strip()
            if sid and sid != "0000000000000000":
                return sid
    except Exception:
        return None
    return None

# --- CSV-Downloader priorisiert die bestätigten Endpunkte ----------
def _try_fetch_csv(base: str, user: str, pwd: str, verify: bool) -> tuple[list[dict], str | None]:
    """
    1) Holt SID via _fritz_get_sid
    2) Probiert zuerst die verifizierten URLs:
         /fon_num/foncalls_list.lua?csv=fon_num/foncalls_list.lua?csv=&max=2000max=5000&sid=...
         /fon_num/foncalls_list.lua?csv=1&sid=...
    3) Fallback: frühere Basis-Varianten (Basic-Auth + verschiedene Pfade)
    """
    timeout = 10

    # 1) SID holen (Challenge-Response)
    sid = _fritz_get_sid(base, user, pwd, verify)
    if sid:
        # 2) Primäre, verifizierte Varianten
        prio_urls = [
            f"{base}/fon_num/foncalls_list.lua?csv=fon_num/foncalls_list.lua?csv=&max=2000max=5000&sid={sid}",
            f"{base}/fon_num/foncalls_list.lua?csv=1&sid={sid}",
        ]
        for url in prio_urls:
            try:
                r = requests.get(url, timeout=timeout, verify=verify)
                if r.status_code == 200 and r.content:
                    items = _fritz_parse_csv(r.content)
                    if items:
                        return items, url
            except Exception:
                pass

    # 3) Fallbacks: Basic-Auth und alternative Pfade
    paths = ["/calllist.lua", "/fon_num/foncalls_list.lua", "/foncalls_list.lua"]
    for rel in paths:
        url = f"{base}{rel}?csv=&max=2000"
        try:
            r = requests.get(url, auth=HTTPBasicAuth(user, pwd), timeout=timeout, verify=verify)
            if r.status_code == 200 and r.content:
                items = _fritz_parse_csv(r.content)
                if items:
                    return items, url
        except Exception:
            pass

    # 4) Falls wir eine SID hatten, probiere die Pfade noch einmal mit SID
    if sid:
        for rel in paths:
            # zwei Varianten: csv=&max=…&sid=…  und csv=1&sid=…
            for tail in (f"?csv=&max=2000&sid={sid}", f"?csv=1&sid={sid}"):
                url = f"{base}{rel}{tail}"
                try:
                    r = requests.get(url, timeout=timeout, verify=verify)
                    if r.status_code == 200 and r.content:
                        items = _fritz_parse_csv(r.content)
                        if items:
                            return items, url
                except Exception:
                    pass

    return [], None

@require_GET
def fritzbox_call_list(request):
    """
    Holt die Anrufliste direkt per Challenge-Response-Login und rendert sie.
    Nutzt den bestätigten Endpunkt:
      /fon_num/foncalls_list.lua?csv=fon_num/foncalls_list.lua?csv=&max=2000max=5000&sid=...
    """
    base, user, pwd, verify = _fritz_env()
    if not user or not pwd:
        messages.error(request, "Fritzbox-Zugangsdaten fehlen (FRITZBOX_USERNAME / FRITZBOX_PASSWORD).")
        return render(request, "crm_core/voip/call_list.html", {"calls": []})

    import hashlib

    try:
        # 1) Challenge holen
        r0 = requests.get(f"{base}/login_sid.lua", timeout=10, verify=verify)
        if r0.status_code != 200:
            messages.error(request, f"Fritzbox login_sid.lua nicht erreichbar (HTTP {r0.status_code}).")
            return render(request, "crm_core/voip/call_list.html", {"calls": []})
        t0 = r0.text
        sC = t0.find("<Challenge>"); eC = t0.find("</Challenge>")
        if sC == -1 or eC == -1:
            messages.error(request, "Challenge in login_sid.lua nicht gefunden.")
            return render(request, "crm_core/voip/call_list.html", {"calls": []})
        challenge = t0[sC+11:eC].strip()

        # 2) Response bauen (UTF-16LE + MD5) und SID holen
        payload = (challenge + "-" + pwd).encode("utf-16le")
        response = f"{challenge}-{hashlib.md5(payload).hexdigest()}"
        r1 = requests.get(f"{base}/login_sid.lua",
                          params={"username": user, "response": response},
                          timeout=10, verify=verify)
        if r1.status_code != 200:
            messages.error(request, f"Fritzbox SID-Login fehlgeschlagen (HTTP {r1.status_code}).")
            return render(request, "crm_core/voip/call_list.html", {"calls": []})

        t1 = r1.text
        sS = t1.find("<SID>"); eS = t1.find("</SID>")
        sid = t1[sS+5:eS].strip() if (sS != -1 and eS != -1) else ""
        if not sid or sid == "0000000000000000":
            messages.error(request, "SID ungültig (Login fehlgeschlagen).")
            return render(request, "crm_core/voip/call_list.html", {"calls": []})

        # 3) CSV ziehen – bestätigter Pfad
        url = f"{base}/fon_num/foncalls_list.lua?csv=fon_num/foncalls_list.lua?csv=&max=2000max=5000&sid={sid}"
        r2 = requests.get(url, timeout=15, verify=verify)
        ct = r2.headers.get("Content-Type", ""); print("FRITZ DEBUG:", r2.status_code, ct, url)
        print("FRITZ DEBUG HEAD:", (r2.text or "")[:160].replace("\n"," "))
        ct = r2.headers.get("Content-Type", "")
        print("FRITZ DEBUG:", r2.status_code, ct, url)
        head_preview = (r2.text or "")[:160].replace("\n", " ")
        print("FRITZ DEBUG HEAD:", head_preview)

        if r2.status_code != 200 or not r2.content:
            messages.error(request, f"Anrufliste nicht abrufbar (HTTP {r2.status_code}).")
            return render(request, "crm_core/voip/call_list.html", {"calls": []})

        # 4) sep=;-Zeile ggf. entfernen, dann parsen
        content = r2.content
        try:
            txt = content.decode("utf-8", errors="ignore")
            if txt.strip().lower().startswith("sep="):
                # erste Zeile abschneiden
                txt = "\n".join(txt.splitlines()[1:])
                content = txt.encode("utf-8", errors="ignore")
        except Exception:
            pass

        items = _fritz_parse_csv(content) or []
        messages.success(request, f"Anrufliste geladen ({len(items)} Einträge).")
        return render(request, "crm_core/voip/call_list.html", {"calls": items})

    except Exception as e:
        messages.error(request, f"Fehler beim Laden der Anrufliste: {e}")
        return render(request, "crm_core/voip/call_list.html", {"calls": []})

# --- Robuster Fritz!Box CSV-Parser (überschreibt ältere Version) ---
def _fritz_parse_csv(blob):
    """
    Erwartet Fritz!Box CSV mit optionaler 'sep=;'-Erstzeile.
    Robust gegen BOM, ISO-8859-1/UFT-8, CRLF. Liefert Liste von Dicts.
    """
    # 1) Bytes -> Text
    if isinstance(blob, (bytes, bytearray)):
        try:
            text = blob.decode("iso-8859-1", errors="ignore")
        except Exception:
            text = blob.decode("utf-8", errors="ignore")
    else:
        text = str(blob or "")

    # 2) BOM entfernen, normalisieren
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    lines = text.splitlines()

    # 3) Optionale 'sep=;' Kopfzeile skippen
    if lines and lines[0].strip().lower().startswith("sep="):
        lines = lines[1:]

    if not lines:
        print("FRITZ PARSER: keine Zeilen nach sep=; / leere Datei")
        return []

    # 4) CSV lesen
    import csv
    reader = csv.reader(lines, delimiter=';')
    rows = list(reader)
    if not rows:
        print("FRITZ PARSER: keine CSV-Zeilen")
        return []

    header = [ (h or "").strip().lower() for h in rows[0] ]
    data = rows[1:]

    print("FRITZ PARSER: header=", header)
    print("FRITZ PARSER: rows=", len(data))

    # 5) Spaltenindizes ermitteln (mit Fallbacks)
    def idx(*cands):
        for c in cands:
            try:
                return header.index(c)
            except ValueError:
                continue
        return None

    i_typ   = idx("typ", "type")
    i_date  = idx("datum", "date")
    i_name  = idx("name")
    i_from  = idx("rufnummer", "caller", "from")
    i_to    = idx("angerufene rufnummer", "called", "to", "zielrufnummer")
    i_own   = idx("eigene rufnummer", "eigenenummer", "ownnumber")
    i_dur   = idx("dauer", "duration")
    i_dev   = idx("gerät", "device", "line", "nebenstelle")

    items = []
    for r in data:
        def g(i):
            return (r[i].strip() if (i is not None and i < len(r)) else "")
        items.append({
            "type":     g(i_typ),
            "date":     g(i_date),
            "name":     g(i_name),
            "caller":   g(i_from),
            "target":   g(i_to),
            "own":      g(i_own),
            "duration": g(i_dur),
            "device":   g(i_dev),
        })
    return items

@csrf_exempt
@require_POST
def call_number_via_sipgate(request):
    """
    Initiates a call via Sipgate Sessions API.
    Requires env: SIPGATE_TOKEN_ID, SIPGATE_TOKEN, SIPGATE_CALLER
    Optional: SIPGATE_DEVICE_ID (default e0)
    """
    def wants_json(req):
        return "application/json" in req.headers.get("Accept", "") or req.headers.get("X-Requested-With") == "fetch"

    number = (request.POST.get("number") or "").strip()
    print("SIPGATE DEBUG: incoming number raw =", number)
    if not number:
        if wants_json(request):
            return JsonResponse({"ok": False, "error": "Nummer fehlt"}, status=400)
        messages.error(request, "Nummer fehlt.")
        return redirect("crm_core:fritzbox_call_list")

    # E.164/normalisieren: Leerzeichen, /, - entfernen
    import re
    callee = re.sub(r"[^\d+]", "", number)
    print("SIPGATE DEBUG: normalized callee =", callee)

    token_id = os.getenv("SIPGATE_TOKEN_ID", "")
    token    = os.getenv("SIPGATE_TOKEN", "")
    device   = os.getenv("SIPGATE_DEVICE_ID", "e0")
    caller   = os.getenv("SIPGATE_CALLER", "")

    if not token_id or not token or not caller:
        msg = "Sipgate-Config unvollständig (SIPGATE_TOKEN_ID / SIPGATE_TOKEN / SIPGATE_CALLER)."
        print("SIPGATE DEBUG:", msg)
        if wants_json(request):
            return JsonResponse({"ok": False, "error": msg}, status=500)
        messages.error(request, msg)
        return redirect("crm_core:fritzbox_call_list")

    url = "https://api.sipgate.com/v2/sessions/calls"
    payload = {"deviceId": device, "caller": caller, "callee": callee}
    print("SIPGATE DEBUG: POST", url, payload)

    try:
        resp = requests.post(url, json=payload, auth=(token_id, token), timeout=15)
        print("SIPGATE DEBUG: status", resp.status_code, "body", resp.text[:300])
        if resp.status_code == 201:
            if wants_json(request):
                return JsonResponse({"ok": True, "message": f"Anruf zu {callee} gestartet."}, status=201)
            messages.success(request, f"Anruf zu {callee} gestartet.")
        else:
            if wants_json(request):
                return JsonResponse({"ok": False, "status": resp.status_code, "error": resp.text}, status=resp.status_code)
            messages.error(request, f"Sipgate-Fehler {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print("SIPGATE DEBUG: exception", e)
        if wants_json(request):
            return JsonResponse({"ok": False, "error": str(e)}, status=500)
        messages.error(request, f"Sipgate-Request fehlgeschlagen: {e}")

    return redirect("crm_core:fritzbox_call_list")

import re
from django.db.models import Q
from .models import CallLog, Contact, Company

def _normalize_phone(s: str) -> str:
    """Einfache Normalisierung: nur Ziffern + führendes + erlauben."""
    if not s:
        return ""
    s = s.strip()
    # deutsche 00… -> +…
    s = re.sub(r'^\s*00', '+', s)
    # alles außer Ziffern und + raus
    s = re.sub(r'[^\d+]', '', s)
    # führende 0 optional in Landesformat überlassen; minimal sauber halten
    return s

def _find_contact_by_number(number: str):
    """Versucht, einen Kontakt zur Nummer zu finden (genau oder suffix-match)."""
    if not number:
        return None, None
    n = _normalize_phone(number)

    # direkte Felder im Contact-Modell anpassen, falls du andere Feldnamen nutzt
    qs = Contact.objects.filter(
        Q(phone__icontains=n) |
        Q(mobile__icontains=n) |
        Q(email__icontains=n) |  # manchmal steht die Nummer in E-Mail-Feld → optional
        Q(notes__icontains=n)
    ).order_by('id')

    if not qs.exists():
        # suffix-Match: letzte 6–8 Ziffern
        tail = re.sub(r'\D', '', n)[-7:]
        if tail:
            qs = Contact.objects.filter(
                Q(phone__icontains=tail) | Q(mobile__icontains=tail)
            ).order_by('id')

    contact = qs.first() if qs.exists() else None
    company = contact.company if (contact and hasattr(contact, "company")) else None
    return contact, company

@csrf_exempt
@require_POST
def call_number_via_sipgate(request):
    """
    Initiates a call via Sipgate Sessions API and logs to CallLog.
    Env: SIPGATE_TOKEN_ID, SIPGATE_TOKEN, SIPGATE_CALLER, [SIPGATE_DEVICE_ID]
    """
    def wants_json(req):
        return "application/json" in req.headers.get("Accept", "") or req.headers.get("X-Requested-With") == "fetch"

    raw_number = (request.POST.get("number") or "").strip()
    callee = _normalize_phone(raw_number)
    print("SIPGATE DEBUG: callee =", callee)
    if not callee:
        msg = "Nummer fehlt oder ungültig."
        if wants_json(request):
            return JsonResponse({"ok": False, "error": msg}, status=400)
        messages.error(request, msg)
        return redirect("crm_core:fritzbox_call_list")

    token_id = os.getenv("SIPGATE_TOKEN_ID", "")
    token    = os.getenv("SIPGATE_TOKEN", "")
    device   = os.getenv("SIPGATE_DEVICE_ID", "e0")
    caller   = _normalize_phone(os.getenv("SIPGATE_CALLER", ""))

    if not token_id or not token or not caller:
        msg = "Sipgate-Config unvollständig (SIPGATE_TOKEN_ID / SIPGATE_TOKEN / SIPGATE_CALLER)."
        if wants_json(request):
            return JsonResponse({"ok": False, "error": msg}, status=500)
        messages.error(request, msg)
        return redirect("crm_core:fritzbox_call_list")

    url = "https://api.sipgate.com/v2/sessions/calls"
    payload = {"deviceId": device, "caller": caller, "callee": callee}

    # Vorab Kontakt ermitteln (best-effort)
    contact, company = _find_contact_by_number(callee)

    try:
        resp = requests.post(url, json=payload, auth=(token_id, token), timeout=15)
        ok = (resp.status_code == 201)

        # CallLog schreiben
        CallLog.objects.create(
            number=callee,
            direction="out",
            status="initiated" if ok else "failed",
            source="sipgate",
            contact=contact,
            company=company,
            raw={"status_code": resp.status_code, "body": resp.text[:1000], "payload": payload},
        )

        if wants_json(request):
            if ok:
                return JsonResponse({"ok": True, "message": f"Anruf zu {callee} gestartet."}, status=201)
            return JsonResponse({"ok": False, "status": resp.status_code, "error": resp.text}, status=resp.status_code)

        if ok:
            messages.success(request, f"Anruf zu {callee} gestartet.")
        else:
            messages.error(request, f"Sipgate-Fehler {resp.status_code}: {resp.text[:200]}")

    except Exception as e:
        # Fehler auch loggen
        CallLog.objects.create(
            number=callee, direction="out", status="failed", source="sipgate",
            contact=contact, company=company, raw={"exception": str(e)}
        )
        if wants_json(request):
            return JsonResponse({"ok": False, "error": str(e)}, status=500)
        messages.error(request, f"Sipgate-Request fehlgeschlagen: {e}")

    return redirect("crm_core:fritzbox_call_list")

# ---------- Robust contact matching ----------
def _contact_phone_fields():
    """Suche sinnvolle Felder im Contact-Modell, die Telefonnnummern enthalten könnten."""
    try:
        fields = [f.name for f in Contact._meta.get_fields() if getattr(f, "attname", f.name)]
    except Exception:
        fields = []
    candidates = [
        "phone", "mobile", "cell", "phone_number", "phone_mobile",
        "telefon", "telefonnummer", "handy", "business_phone", "work_phone",
        "home_phone", "fax", "tel", "telefon_privat", "telefon_geschaeft",
        "notes", "note", "description", "about"
    ]
    return [f for f in candidates if f in fields]

def _normalize_phone(s: str) -> str:
    import re
    if not s:
        return ""
    s = s.strip()
    s = re.sub(r'^\s*00', '+', s)           # 00… -> +…
    s = re.sub(r'[^\d+]', '', s)            # nur Ziffern/+ behalten
    return s

def _find_contact_by_number(number: str):
    """Sucht Contact anhand vorhandener Felder. Fällt auf Suffix-Match zurück."""
    from django.db.models import Q
    n = _normalize_phone(number)
    if not n:
        return None, None

    fields = _contact_phone_fields()
    q = Q()
    for f in fields:
        q |= Q(**{f"{f}__icontains": n})

    qs = Contact.objects.filter(q) if q else Contact.objects.none()
    if not qs.exists():
        # Suffix-Match: letzte 7 Ziffern
        tail_digits = "".join(ch for ch in n if ch.isdigit())[-7:]
        if tail_digits:
            q2 = Q()
            for f in fields:
                q2 |= Q(**{f"{f}__icontains": tail_digits})
            qs = Contact.objects.filter(q2) if q2 else Contact.objects.none()

    contact = qs.first() if qs.exists() else None
    company = getattr(contact, "company", None) if contact else None
    return contact, company

@csrf_exempt
@require_POST
def call_number_via_sipgate(request):
    """
    Initiates a call via Sipgate Sessions API and logs to CallLog.
    """
    from django.http import JsonResponse

    def wants_json(req):
        return "application/json" in req.headers.get("Accept", "") or req.headers.get("X-Requested-With") == "fetch"

    raw_number = (request.POST.get("number") or "").strip()
    callee = _normalize_phone(raw_number)
    if not callee:
        msg = "Nummer fehlt oder ungültig."
        if wants_json(request):
            return JsonResponse({"ok": False, "error": msg}, status=400)
        messages.error(request, msg)
        return redirect("crm_core:fritzbox_call_list")

    token_id = os.getenv("SIPGATE_TOKEN_ID", "")
    token    = os.getenv("SIPGATE_TOKEN", "")
    device   = os.getenv("SIPGATE_DEVICE_ID", "e0")
    caller   = _normalize_phone(os.getenv("SIPGATE_CALLER", ""))

    if not token_id or not token or not caller:
        msg = "Sipgate-Config unvollständig (SIPGATE_TOKEN_ID / SIPGATE_TOKEN / SIPGATE_CALLER)."
        if wants_json(request):
            return JsonResponse({"ok": False, "error": msg}, status=500)
        messages.error(request, msg)
        return redirect("crm_core:fritzbox_call_list")

    # Kontakt vorab versuchen zu finden (best effort)
    contact, company = _find_contact_by_number(callee)

    url = "https://api.sipgate.com/v2/sessions/calls"
    payload = {"deviceId": device, "caller": caller, "callee": callee}

    # Standardwerte für Logging
    log_kwargs = dict(
        number=callee, direction="out", source="sipgate",
        contact=contact, company=company
    )

    try:
        resp = requests.post(url, json=payload, auth=(token_id, token), timeout=15)
        ok = (resp.status_code == 201)
        status = "initiated" if ok else "failed"

        # CallLog anlegen, Fehler abfangen (z. B. wenn Tabelle fehlt)
        try:
            CallLog.objects.create(**log_kwargs, status=status, raw={
                "status_code": resp.status_code,
                "body": resp.text[:1000],
                "payload": payload
            })
        except Exception as e:
            print("CALLLOG DEBUG: konnte Log nicht schreiben:", e)

        if wants_json(request):
            if ok:
                return JsonResponse({"ok": True, "message": f"Anruf zu {callee} gestartet."}, status=201)
            return JsonResponse({"ok": False, "status": resp.status_code, "error": resp.text}, status=resp.status_code)

        if ok:
            messages.success(request, f"Anruf zu {callee} gestartet.")
        else:
            messages.error(request, f"Sipgate-Fehler {resp.status_code}: {resp.text[:200]}")

    except Exception as e:
        print("SIPGATE DEBUG: exception", e)
        try:
            CallLog.objects.create(**log_kwargs, status="failed", raw={"exception": str(e)})
        except Exception as ee:
            print("CALLLOG DEBUG: konnte Fehler-Log nicht schreiben:", ee)

        if wants_json(request):
            return JsonResponse({"ok": False, "error": str(e)}, status=500)
        messages.error(request, f"Sipgate-Request fehlgeschlagen: {e}")

    return redirect("crm_core:fritzbox_call_list")

# ---- Robuster Token-Finder (überschreibt frühere Definitionen) ----
def _require_token(request):
    """
    Holt einen Microsoft Graph OAuth Token aus Session oder allauth.
    Generisch: nimmt den neuesten SocialToken des Users, egal welcher Provider-Slug.
    """
    try:
        print("🟢 Benutzer:", request.user, "auth:", request.user.is_authenticated)
        # 1) Session
        tok = request.session.get("graph_token")
        if tok:
            print("🟢 Session-Token gefunden (gekürzt):", tok[:20], "...")
            return tok

        if not request.user.is_authenticated:
            print("🔴 User nicht eingeloggt (Django)")
            return None

        # 2) Neuestes SocialToken des Users
        from allauth.socialaccount.models import SocialToken
        token = (SocialToken.objects
                 .filter(account__user=request.user)
                 .order_by("-id")
                 .first())
        if token and token.token:
            request.session["graph_token"] = token.token
            print("🟢 SocialToken gefunden (Provider:", token.account.provider, ")")
            return token.token

        print("🔴 Kein SocialToken gefunden")
        return None
    except Exception as e:
        print("🔴 Ausnahme in _require_token:", e)
        return None

@require_POST
def email_attachment_save(request, message_id: str, attachment_id: str):
    """
    Lädt einen E-Mail-Anhang via MS Graph und speichert ihn im Dateimanager (MEDIA_ROOT).
    """
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_detail", message_id=message_id)

    r = _graph_get(token, f"/me/messages/{message_id}/attachments/{attachment_id}")
    if r.status_code != 200:
        messages.error(request, f"Anhang konnte nicht geladen werden ({r.status_code}).")
        return redirect("crm_core:email_detail", message_id=message_id)

    att = r.json()
    content_b64 = att.get("contentBytes")
    name = att.get("name") or "attachment.bin"

    if not content_b64:
        messages.error(request, "Kein Dateiinhalt im Anhang (kein fileAttachment).")
        return redirect("crm_core:email_detail", message_id=message_id)

    # Dateiname säubern
    import re, unicodedata
    safe = unicodedata.normalize("NFKD", name)
    safe = "".join(ch for ch in safe if ch.isalnum() or ch in (".","-","_"," "))
    safe = safe.strip().replace(" ", "_") or "attachment.bin"

    # Zielpfad bestimmen (MEDIA_ROOT) & Kollision vermeiden
    base = _media_root()
    base.mkdir(parents=True, exist_ok=True)
    dest = base / safe
    if dest.exists():
        stem, suffix = dest.stem, dest.suffix
        i = 1
        while True:
            cand = base / f"{stem}_{i}{suffix}"
            if not cand.exists():
                dest = cand
                break
            i += 1

    try:
        data = base64.b64decode(content_b64)
        with dest.open("wb") as f:
            f.write(data)
    except Exception as e:
        messages.error(request, f"Speichern fehlgeschlagen: {e}")
        return redirect("crm_core:email_detail", message_id=message_id)

    messages.success(request, f'Anhang gespeichert als {dest.name}.')
    return redirect("crm_core:files_list")

def _split_name(full: str) -> tuple[str, str]:
    full = (full or "").strip()
    if not full:
        return "", ""
    parts = full.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

@require_http_methods(["GET", "POST"])
def contact_create_from_email(request):
    """
    Erstellt einen Kontakt basierend auf Maildaten.
    - GET mit ?auto=1&name=...&email=... legt direkt an (wenn noch nicht vorhanden).
    - Ohne auto=1 zeigt sie ein Formular mit Initialwerten.
    """
    name = (request.GET.get("name") or "").strip()
    email = (request.GET.get("email") or "").strip()

    # AUTO: direkt anlegen / zum vorhandenen springen
    if request.method == "GET" and request.GET.get("auto") == "1" and email:
        from .models import Contact  # sicherheitshalber lokal importieren
        existing = Contact.objects.filter(email__iexact=email).first()
        if existing:
            messages.info(request, "Kontakt existiert bereits.")
            return redirect("crm_core:contact_detail", pk=existing.pk)
        first, last = _split_name(name)
        try:
            c = Contact(first_name=first, last_name=last, email=email)
            c.save()
            messages.success(request, "Kontakt aus E-Mail erstellt.")
            return redirect("crm_core:contact_detail", pk=c.pk)
        except Exception as e:
            messages.error(request, f"Automatisches Erstellen fehlgeschlagen: {e}")

    # Formular-Fallback (Initialwerte aus GET)
    initial_data = {}
    if name:
        f, l = _split_name(name)
        initial_data["first_name"] = f
        if l:
            initial_data["last_name"] = l
    if email:
        initial_data["email"] = email

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            messages.success(request, "Kontakt wurde erstellt.")
            return redirect("crm_core:contact_detail", pk=contact.pk)
    else:
        form = ContactForm(initial=initial_data)

    return render(request, "crm_core/contact_form.html", {"form": form})

from django.views.decorators.http import require_GET

def _split_name(full: str) -> tuple[str, str]:
    full = (full or "").strip()
    if not full:
        return "", ""
    parts = full.split()
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])

@require_GET
def email_contact_quickadd(request, message_id: str):
    """
    Holt Absender (From/Sender) via MS Graph für message_id und
    legt Contact an (falls noch nicht vorhanden). Leitet zum Kontakt um.
    """
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:email_detail", message_id=message_id)

    # nur die Felder holen, die wir brauchen
    r = _graph_get(token, f"/me/messages/{message_id}", params={"$select": "from,sender"})
    if r.status_code != 200:
        messages.error(request, f"E-Mail konnte nicht geladen werden ({r.status_code}).")
        return redirect("crm_core:email_detail", message_id=message_id)

    data = r.json() or {}
    from_info = (data.get("from") or {}).get("emailAddress") or {}
    if not from_info.get("address"):
        # Fallback: "sender"
        from_info = (data.get("sender") or {}).get("emailAddress") or {}

    email = (from_info.get("address") or "").strip()
    name  = (from_info.get("name") or "").strip()

    if not email:
        messages.error(request, "Kein gültiger Absender gefunden.")
        return redirect("crm_core:email_detail", message_id=message_id)

    # Kontakt suchen/erstellen
    try:
        existing = Contact.objects.filter(email__iexact=email).first()
        if existing:
            messages.info(request, "Kontakt existiert bereits.")
            return redirect("crm_core:contact_detail", pk=existing.pk)

        first, last = _split_name(name)
        c = Contact(first_name=first, last_name=last, email=email)
        c.save()
        messages.success(request, f"Kontakt angelegt: {c.first_name} {c.last_name or ''}".strip() or email)
        return redirect("crm_core:contact_detail", pk=c.pk)
    except Exception as e:
        messages.error(request, f"Kontakt konnte nicht erstellt werden: {e}")
        return redirect("crm_core:email_detail", message_id=message_id)

@require_GET
def calendar_list(request):
    """
    Zeigt Termine in einem sinnvollen Fenster (heute-30d .. heute+90d).
    Nutzt /me/calendarView und bereitet Anzeige-Felder auf.
    """
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:dashboard")

    from datetime import timedelta
    now = dj_tz.now()
    start = now - timedelta(days=1)
    end   = now + timedelta(days=90)

    params = {
        "startDateTime": _utc_iso(start),
        "endDateTime":   _utc_iso(end),
        "$orderby":      "start/dateTime asc",
        "$top":          "200",
    }
    r = _graph_get(token, "/me/calendarView", params=params)
    if r.status_code != 200:
        messages.error(request, f"Fehler beim Laden der Termine ({r.status_code}).")
        return redirect("crm_core:dashboard")

    events = r.json().get("value", [])
    events_disp = []
    for _e in events:
        sd  = _dt_to_str((_e.get("start") or {}))
        ed  = _dt_to_str((_e.get("end") or {}))
        loc = (_e.get("location") or {}).get("displayName")
        _e["start_display"]      = sd
        _e["end_display"]        = ed
        _e["location_display"]   = loc
        _e["is_all_day_display"] = "Ja" if _e.get("isAllDay") else "Nein"
        events_disp.append(_e)

    return render(request, "crm_core/calendar/index.html", {"events": events_disp})

@require_GET
def calendar_list(request):
    """
    Zeigt Termine im Fenster (heute-1d .. heute+90d).
    Zeiten werden zu 'TT.MM.JJJJ HH:MM' formatiert und als start_display/end_display geliefert.
    Zusätzlich werden start/end selbst als String gesetzt, damit alte Templates nicht mehr ISO zeigen.
    """
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:dashboard")

    from datetime import timedelta
    now = dj_tz.now()
    start = now - timedelta(days=1)
    end   = now + timedelta(days=90)

    params = {
        "startDateTime": _utc_iso(start),
        "endDateTime":   _utc_iso(end),
        "$orderby":      "start/dateTime asc",
        "$top":          "200",
    }
    r = _graph_get(token, "/me/calendarView", params=params)
    if r.status_code != 200:
        messages.error(request, f"Fehler beim Laden der Termine ({r.status_code}).")
        return redirect("crm_core:dashboard")

    events = r.json().get("value", [])
    events_disp = []
    for _e in events:
        sd  = _dt_to_str((_e.get("start") or {}))  # -> "TT.MM.JJJJ HH:MM"
        ed  = _dt_to_str((_e.get("end") or {}))
        loc = (_e.get("location") or {}).get("displayName")

        # Anzeige-Felder
        _e["start_display"]      = sd
        _e["end_display"]        = ed
        _e["location_display"]   = loc
        _e["is_all_day_display"] = "Ja" if _e.get("isAllDay") else "Nein"

        # Fallback: start/end als bereits formatierte Strings setzen,
        # falls Templates noch {{ e.start.dateTime }} o.ä. verwenden.
        _e["start"] = sd
        _e["end"]   = ed

        events_disp.append(_e)

    return render(request, "crm_core/calendar/index.html", {"events": events_disp})

# --- robuste Neu-Implementierung: ISO -> "TT.MM.JJJJ HH:MM" ---
def _dt_to_str(graph_dt: Dict[str, str]) -> str:
    """
    MS Graph {"dateTime":"...","timeZone":"..."} -> lokale Zeit "dd.mm.yyyy HH:MM".
    Kommt ohne python-dateutil aus. Handhabt 'Z' und 7-stellige Fractional Seconds.
    """
    try:
        dt_str = ((graph_dt or {}).get("dateTime") or "").strip()
        if not dt_str:
            return ""

        # 'Z' -> '+00:00'
        s = dt_str.replace("Z", "+00:00")

        # 7-stellige Fractional Seconds auf 6 kürzen, damit fromisoformat klappt
        import re
        m = re.match(r"^(.*T\d{2}:\d{2}:\d{2})(\.\d+)?(.*)$", s)
        if m:
            frac = m.group(2) or ""
            if len(frac) > 7:  # inkl. Punkt
                frac = "." + frac[1:7]
            s = m.group(1) + frac + (m.group(3) or "")

        from datetime import datetime as _dt
        from django.utils import timezone as dj_tz

        dt = _dt.fromisoformat(s)

        # nach aware/local konvertieren
        if dj_tz.is_aware(dt):
            local_dt = dj_tz.localtime(dt)
        else:
            local_dt = dj_tz.localtime(dj_tz.make_aware(dt, dj_tz.utc))

        return local_dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        # Fallback: Rohwert anzeigen
        return (graph_dt or {}).get("dateTime") or ""

# --- robuste ISO->"TT.MM.JJJJ HH:MM" Formatierung ---
def _dt_to_str(graph_dt: Dict[str, str]) -> str:
    """
    MS Graph {"dateTime":"...","timeZone":"..."} -> "dd.mm.yyyy HH:MM" in lokaler TZ.
    Handhabt 'Z', Offsets, 7-stellige Millisekunden. Nutzt dateutil wenn vorhanden.
    """
    try:
        dt_str = ((graph_dt or {}).get("dateTime") or "").strip()
        if not dt_str:
            return ""
        s = dt_str.replace("Z", "+00:00")

        # 7-stellige Fractional Seconds auf 6 kürzen (fromisoformat)
        import re
        m = re.match(r"^(.*T\d{2}:\d{2}:\d{2})(\.\d+)?(.*)$", s)
        if m:
            frac = m.group(2) or ""
            if len(frac) > 7:  # inkl. Punkt
                frac = "." + frac[1:7]
            s = m.group(1) + frac + (m.group(3) or "")

        from django.utils import timezone as dj_tz
        try:
            from dateutil import parser as _parser  # optional
            dt = _parser.isoparse(s)
        except Exception:
            from datetime import datetime as _dt
            dt = _dt.fromisoformat(s)

        if dj_tz.is_naive(dt):
            dt = dj_tz.make_aware(dt, dj_tz.utc)
        local_dt = dj_tz.localtime(dt)
        return local_dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return (graph_dt or {}).get("dateTime") or ""

@require_GET
def calendar_list(request):
    """
    Termine im Fenster (heute-1d .. heute+90d), mit "TT.MM.JJJJ HH:MM".
    Rendert gezielt crm_core/calendar/index.html.
    """
    token = _require_token(request)
    if not token:
        messages.error(request, "Nicht bei Microsoft angemeldet.")
        return redirect("crm_core:dashboard")

    from datetime import timedelta
    now = dj_tz.now()
    start = now - timedelta(days=1)
    end   = now + timedelta(days=90)

    params = {
        "startDateTime": _utc_iso(start),
        "endDateTime":   _utc_iso(end),
        "$orderby":      "start/dateTime asc",
        "$top":          "200",
    }
    r = _graph_get(token, "/me/calendarView", params=params)
    if r.status_code != 200:
        messages.error(request, f"Fehler beim Laden der Termine ({r.status_code}).")
        return redirect("crm_core:dashboard")

    events = r.json().get("value", [])
    events_disp = []
    for _e in events:
        sd  = _dt_to_str((_e.get("start") or {}))
        ed  = _dt_to_str((_e.get("end") or {}))
        loc = (_e.get("location") or {}).get("displayName")

        _e["start_display"]      = sd
        _e["end_display"]        = ed
        _e["location_display"]   = loc
        _e["is_all_day_display"] = "Ja" if _e.get("isAllDay") else "Nein"

        # Fallback: auch 'start'/'end' selbst zu Strings machen,
        # falls ein altes Template noch {{ e.start.dateTime }} nutzt.
        _e["start"] = sd
        _e["end"]   = ed

        events_disp.append(_e)

    return render(request, "crm_core/calendar/index.html", {"events": events_disp})

# --- endgültig robuste Anzeige-Formatierung (ohne Parser-Zwang) ---
def _dt_to_str(graph_dt: Dict[str, str]) -> str:
    """
    MS Graph {"dateTime": "...", "timeZone": "..."} -> "dd.mm.yyyy HH:MM".
    Fällt niemals auf ISO zurück, sondern formatiert direkt per String-Slicing,
    wenn Parser scheitert oder die Zeitzone fehlt.
    """
    dt_str = ((graph_dt or {}).get("dateTime") or "").strip()
    if not dt_str:
        return ""
    # Schneller Weg: "YYYY-MM-DDTHH:MM" vorhanden?
    try:
        if len(dt_str) >= 16 and dt_str[4] == "-" and dt_str[7] == "-" and dt_str[10] == "T":
            yyyy = dt_str[0:4]; mm = dt_str[5:7]; dd = dt_str[8:10]; hh = dt_str[11:13]; mi = dt_str[14:16]
            return f"{dd}.{mm}.{yyyy} {hh}:{mi}"
    except Exception:
        pass

    # Parser-Weg (optional), falls vorhanden – Ergebnis dennoch nur HH:MM ausgeben
    try:
        from dateutil import parser as _parser  # optional
        from django.utils import timezone as dj_tz
        s = dt_str.replace("Z", "+00:00")
        # 7-stellige Fractional Seconds auf 6 kürzen
        import re
        m = re.match(r"^(.*T\d{2}:\d{2}:\d{2})(\.\d+)?(.*)$", s)
        if m:
            frac = m.group(2) or ""
            if len(frac) > 7:  # inkl. Punkt
                frac = "." + frac[1:7]
            s = m.group(1) + frac + (m.group(3) or "")
        dt = _parser.isoparse(s)
        if dj_tz.is_naive(dt):
            dt = dj_tz.make_aware(dt, dj_tz.utc)
        local_dt = dj_tz.localtime(dt)
        return local_dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        # Letzter Fallback: rohe ISO-Strings bestmöglich schneiden
        try:
            if "T" in dt_str:
                date_part, time_part = dt_str.split("T", 1)
                yyyy, mm, dd = date_part.split("-", 2)
                hh, mi = time_part[0:2], time_part[3:5]
                return f"{dd}.{mm}.{yyyy} {hh}:{mi}"
        except Exception:
            pass
        return dt_str  # allerletzter Notnagel
# --- finale, TZ-korrekte Anzeige: "dd.mm.yyyy HH:MM" ---
def _dt_to_str(graph_dt: Dict[str, str]) -> str:
    """
    Erwartet MS Graph-Objekt {"dateTime": "...", "timeZone": "..."}.
    - parsed ISO (inkl. 'Z' und Offsets)
    - wenn tzinfo fehlt: nutzt graph_dt["timeZone"] (Windows→IANA Mapping)
    - konvertiert in Django-Local TZ (settings.TIME_ZONE)
    - formatiert als "dd.mm.yyyy HH:MM"
    """
    dt_raw = ((graph_dt or {}).get("dateTime") or "").strip()
    tz_id  = ((graph_dt or {}).get("timeZone") or "").strip()
    if not dt_raw:
        return ""

    # 1) ISO fit machen: 'Z' → '+00:00', 7-stellige Mikrosekunden auf 6 kürzen
    s = dt_raw.replace("Z", "+00:00")
    try:
        import re
        m = re.match(r"^(.*T\d{2}:\d{2}:\d{2})(\.\d+)?(.*)$", s)
        if m:
            frac = m.group(2) or ""
            if len(frac) > 7:
                frac = "." + frac[1:7]
            s = m.group(1) + frac + (m.group(3) or "")
    except Exception:
        pass

    # 2) parsen (mit dateutil, Fallback stdlib)
    from django.utils import timezone as dj_tz
    try:
        try:
            from dateutil import parser as _parser  # bevorzugt
            dt = _parser.isoparse(s)
        except Exception:
            from datetime import datetime as _dt
            dt = _dt.fromisoformat(s)

        # 3) fehlende tzinfo? -> aus Graph-timeZone ableiten
        if dj_tz.is_naive(dt):
            tzinfo = None
            # Windows→IANA Mapping (reicht für D/AT/CH)
            W2I = {
                "W. Europe Standard Time": "Europe/Berlin",
                "Romance Standard Time": "Europe/Paris",
                "GMT Standard Time": "Europe/London",
                "UTC": "UTC",
            }
            iana = W2I.get(tz_id, None)
            if iana:
                try:
                    from zoneinfo import ZoneInfo
                    tzinfo = ZoneInfo(iana if iana != "UTC" else "UTC")
                except Exception:
                    tzinfo = dj_tz.utc if iana == "UTC" else dj_tz.get_current_timezone()
            else:
                # wenn keine Angabe: konservativ als UTC interpretieren (Graph liefert häufig UTC)
                tzinfo = dj_tz.utc
            dt = dj_tz.make_aware(dt, tzinfo)

        # 4) in lokale Django-TZ wandeln und formatieren
        local_dt = dj_tz.localtime(dt, dj_tz.get_current_timezone())
        return local_dt.strftime("%d.%m.%Y %H:%M")

    except Exception:
        # ultima ratio: best effort Slicing (ohne TZ-Korrektur)
        try:
            if len(dt_raw) >= 16 and dt_raw[4] == "-" and dt_raw[7] == "-" and dt_raw[10] == "T":
                yyyy, mm, dd = dt_raw[0:4], dt_raw[5:7], dt_raw[8:10]
                hh, mi = dt_raw[11:13], dt_raw[14:16]
                return f"{dd}.{mm}.{yyyy} {hh}:{mi}"
        except Exception:
            pass
        return dt_raw

def _sanitize_mail_html(html: str) -> str:
    """
    Sehr schlichtes Sanitizing: <script> entfernen + on* Handler strippen.
    Für "richtig" besser django-bleach o.Ä. verwenden.
    """
    if not html:
        return ""
    try:
        html = re.sub(r'(?is)<script[^>]*>.*?</script>', '', html)
        html = re.sub(r'(?is)\son[a-zA-Z]+\s*=\s*"(.*?)"', '', html)
        html = re.sub(r"(?is)\son[a-zA-Z]+\s*=\s*'(.*?)'", '', html)
        return html
    except Exception:
        return html

def _sanitize_mail_html(html: str) -> str:
    """
    Sehr schlichtes Sanitizing: <script> entfernen + on* Handler strippen.
    Für "richtig" besser django-bleach o.Ä. verwenden.
    """
    if not html:
        return ""
    try:
        html = re.sub(r'(?is)<script[^>]*>.*?</script>', '', html)
        html = re.sub(r'(?is)\son[a-zA-Z]+\s*=\s*"(.*?)"', '', html)
        html = re.sub(r"(?is)\son[a-zA-Z]+\s*=\s*'(.*?)'", '', html)
        return html
    except Exception:
        return html

def email_view(request, message_id: str):
    """
    Einzelne Mail anzeigen (Betreff, Absender, Datum, Body).
    """
    try:
        s = get_ms_session(request.user)
        url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        params = {
            "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,hasAttachments,webLink,bodyPreview,body"
        }
        resp = s.get(url, params=params)
        resp.raise_for_status()
        data = resp.json() or {}

        dfrom = (data.get("from") or {}).get("emailAddress") or {}
        body = data.get("body") or {}
        content_type = (body.get("contentType") or "").lower()
        content = body.get("content") or ""

        if content_type == "html":
            content = _sanitize_mail_html(content)
        else:
            # einfache Text-zu-HTML Wandlung
            content = "<pre style='white-space:pre-wrap;margin:0'>" + (content or data.get("bodyPreview") or "") + "</pre>"

        return render(request, "crm_core/email/view.html", {
            "id": data.get("id"),
            "subject": data.get("subject") or "(kein Betreff)",
            "from_name": dfrom.get("name") or dfrom.get("address") or "",
            "from_email": dfrom.get("address") or "",
            "when": data.get("receivedDateTime") or "",
            "weblink": data.get("webLink") or "",
            "html": content,
            "has_attachments": bool(data.get("hasAttachments")),
        })
    except Exception as e:
        logging.exception("email_view failed: %s", e)
        return HttpResponse(f"Fehler beim Laden der Mail: {e}", status=500)

def _sanitize_mail_html(html: str) -> str:
    """
    Sehr schlichtes Sanitizing: <script> entfernen + on* Handler strippen.
    Für "richtig" besser django-bleach o.Ä. verwenden.
    """
    if not html:
        return ""
    try:
        html = re.sub(r'(?is)<script[^>]*>.*?</script>', '', html)
        html = re.sub(r'(?is)\son[a-zA-Z]+\s*=\s*"(.*?)"', '', html)
        html = re.sub(r"(?is)\son[a-zA-Z]+\s*=\s*'(.*?)'", '', html)
        return html
    except Exception:
        return html

def email_view(request, message_id: str):
    """
    Einzelne Mail anzeigen (Betreff, Absender, Datum, Body).
    """
    try:
        s = get_ms_session(request.user)
        url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        params = {
            "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,hasAttachments,webLink,bodyPreview,body"
        }
        resp = s.get(url, params=params)
        resp.raise_for_status()
        data = resp.json() or {}

        dfrom = (data.get("from") or {}).get("emailAddress") or {}
        body = data.get("body") or {}
        content_type = (body.get("contentType") or "").lower()
        content = body.get("content") or ""

        if content_type == "html":
            content = _sanitize_mail_html(content)
        else:
            # einfache Text-zu-HTML Wandlung
            content = "<pre style='white-space:pre-wrap;margin:0'>" + (content or data.get("bodyPreview") or "") + "</pre>"

        return render(request, "crm_core/email/view.html", {
            "id": data.get("id"),
            "subject": data.get("subject") or "(kein Betreff)",
            "from_name": dfrom.get("name") or dfrom.get("address") or "",
            "from_email": dfrom.get("address") or "",
            "when": data.get("receivedDateTime") or "",
            "weblink": data.get("webLink") or "",
            "html": content,
            "has_attachments": bool(data.get("hasAttachments")),
        })
    except Exception as e:
        logging.exception("email_view failed: %s", e)
        return HttpResponse(f"Fehler beim Laden der Mail: {e}", status=500)

def email_reply(request, message_id: str):
    """
    Platzhalter für Antworten – vorerst nicht re-implementiert.
    """
    return HttpResponse("Reply ist vorübergehend deaktiviert.", status=501)

def _sanitize_mail_html(html: str) -> str:
    """
    Sehr schlichtes Sanitizing: <script> entfernen + on* Handler strippen.
    Für "richtig" besser django-bleach o.Ä. verwenden.
    """
    if not html:
        return ""
    try:
        html = re.sub(r'(?is)<script[^>]*>.*?</script>', '', html)
        html = re.sub(r'(?is)\son[a-zA-Z]+\s*=\s*"(.*?)"', '', html)
        html = re.sub(r"(?is)\son[a-zA-Z]+\s*=\s*'(.*?)'", '', html)
        return html
    except Exception:
        return html

def email_view(request, message_id: str):
    """
    Einzelne Mail anzeigen (Betreff, Absender, Datum, Body).
    """
    try:
        s = get_ms_session(request.user)
        url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}"
        params = {
            "$select": "id,subject,from,toRecipients,ccRecipients,receivedDateTime,hasAttachments,webLink,bodyPreview,body"
        }
        resp = s.get(url, params=params)
        resp.raise_for_status()
        data = resp.json() or {}

        dfrom = (data.get("from") or {}).get("emailAddress") or {}
        body = data.get("body") or {}
        content_type = (body.get("contentType") or "").lower()
        content = body.get("content") or ""

        if content_type == "html":
            content = _sanitize_mail_html(content)
        else:
            # einfache Text-zu-HTML Wandlung
            content = "<pre style='white-space:pre-wrap;margin:0'>" + (content or data.get("bodyPreview") or "") + "</pre>"

        return render(request, "crm_core/email/view.html", {
            "id": data.get("id"),
            "subject": data.get("subject") or "(kein Betreff)",
            "from_name": dfrom.get("name") or dfrom.get("address") or "",
            "from_email": dfrom.get("address") or "",
            "when": data.get("receivedDateTime") or "",
            "weblink": data.get("webLink") or "",
            "html": content,
            "has_attachments": bool(data.get("hasAttachments")),
        })
    except Exception as e:
        logging.exception("email_view failed: %s", e)
        return HttpResponse(f"Fehler beim Laden der Mail: {e}", status=500)

def email_reply(request, message_id: str):
    """
    Platzhalter für Antworten – vorerst nicht re-implementiert.
    """
    return HttpResponse("Reply ist vorübergehend deaktiviert.", status=501)

def email_sent(request):
    """
    Sehr einfache Sent-Ansicht (Platzhalter).
    """
    try:
        s = get_ms_session(request.user)
        url = "https://graph.microsoft.com/v1.0/me/mailFolders('sentitems')/messages"
        params = {
            "$select": "id,subject,from,receivedDateTime,hasAttachments",
            "$orderby": "receivedDateTime desc",
            "$top": "20",
        }
        resp = s.get(url, params=params)
        resp.raise_for_status()
        data = resp.json() or {}
        items = []
        for it in (data.get("value") or []):
            dfrom = (it.get("from") or {}).get("emailAddress") or {}
            items.append({
                "id": it.get("id"),
                "subject": it.get("subject") or "(kein Betreff)",
                "from_name": dfrom.get("name") or dfrom.get("address") or "",
                "from_email": dfrom.get("address") or "",
                "when": it.get("receivedDateTime") or "",
                "has_attachments": bool(it.get("hasAttachments")),
            })
        return render(request, "crm_core/email/inbox.html", {
            "items": items, "skip": 0, "top": 20,
            "prev_skip": None, "next_skip": None,
            "error": None,
        })
    except Exception as e:
        logging.exception("email_sent failed: %s", e)
        return HttpResponse(f"Fehler beim Laden 'Gesendet': {e}", status=500)

# --- Mailimport Bridge (Debug) ---
def draft_from_email_bridge(request):
    # Frühe Probe ohne jegliche Abhängigkeiten
    if request.GET.get("probe") == "1":
        return HttpResponse("BRIDGE probe OK")
    try:
        # Import erst jetzt, damit Importfehler sichtbar werden
        from . import views_mailimport as MI  # type: ignore
    except Exception as ex:
        import traceback, html
        tb = traceback.format_exc()
        print("BRIDGE import error:\n", tb)
        return HttpResponse("<h3>BRIDGE ImportError</h3><pre>%s</pre>" % html.escape(tb), status=500)
    try:
        # An die eigentliche Logik weiterreichen
        return MI.from_email(request)
    except Exception:
        import traceback, html
        tb = traceback.format_exc()
        print("BRIDGE call error:\n", tb)
        return HttpResponse("<h3>BRIDGE CallError</h3><pre>%s</pre>" % html.escape(tb), status=500)
