import base64, os, re, requests
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import redirect
from django.utils import timezone

try:
    from allauth.socialaccount.models import SocialToken
except Exception:
    SocialToken = None

def _sanitize(name: str, repl: str = "_") -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]+', repl, name)
    name = re.sub(r"\s+", " ", name)
    return name[:180] if len(name) > 180 else name

def _save_base() -> Path:
    return Path(getattr(settings, "INBOX_SAVE_DIR", "/srv/mycrm/files/inbox"))

def _graph_token_for(user):
    if SocialToken is None:
        return None
    tok = (SocialToken.objects
           .filter(account__user=user, account__provider__in=["microsoft","azuread"])
           .order_by("-expires_at")
           .first())
    return tok.token if tok else None

def _graph_headers(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}

def _graph_delete(user, message_id: str):
    token = _graph_token_for(user)
    if not token:
        return False, "Kein MS Graph Token"
    r = requests.delete(
        f"https://graph.microsoft.com/v1.0/me/messages/{message_id}",
        headers=_graph_headers(token), timeout=20
    )
    if r.status_code in (204, 202):
        return True, None
    return False, f"Graph DELETE {r.status_code}: {r.text[:300]}"

def _graph_save_atts(user, message_id: str):
    token = _graph_token_for(user)
    if not token:
        return False, "Kein MS Graph Token"

    # Meta (Betreff/Datum)
    r = requests.get(
        f"https://graph.microsoft.com/v1.0/me/messages/{message_id}?$select=subject,receivedDateTime",
        headers=_graph_headers(token), timeout=20
    )
    if r.status_code != 200:
        return False, f"Graph GET message {r.status_code}: {r.text[:300]}"
    meta = r.json()
    subject = meta.get("subject", f"message-{message_id}")
    date_part = (meta.get("receivedDateTime") or "")[:10] or "unknown-date"  # YYYY-MM-DD

    # Anhänge
    r = requests.get(
        f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments?$top=200",
        headers=_graph_headers(token), timeout=30
    )
    if r.status_code != 200:
        return False, f"Graph GET attachments {r.status_code}: {r.text[:300]}"
    value = r.json().get("value", [])

    base = _save_base() / date_part / _sanitize(subject)
    base.mkdir(parents=True, exist_ok=True)

    saved = []
    for att in value:
        if att.get("@odata.type") != "#microsoft.graph.fileAttachment":
            continue
        name = _sanitize(att.get("name") or "attachment.bin")
        b64  = att.get("contentBytes")
        if not b64:
            continue
        dest = base / name
        stem, ext = os.path.splitext(name)
        cnt = 1
        while dest.exists() and cnt < 1000:
            dest = base / f"{stem} ({cnt}){ext}"
            cnt += 1
        with open(dest, "wb") as f:
            f.write(base64.b64decode(b64))
        saved.append(str(dest))

    if not saved:
        return False, "Keine Datei-Anhänge gefunden."
    return True, f"Gespeichert in: {base}"

# --- IMAP Fallback (nur falls in settings konfiguriert) ---
def _imap_cfg():
    host = getattr(settings, "IMAP_HOST", None)
    user = getattr(settings, "IMAP_USER", None)
    pwd  = getattr(settings, "IMAP_PASSWORD", None)
    ssl  = getattr(settings, "IMAP_SSL", True)
    return (host and user and pwd), (host, user, pwd, ssl)

def _imap_delete(uid: str):
    ok, cfg = _imap_cfg()
    if not ok:
        return False, "IMAP nicht konfiguriert"
    import imaplib
    host, user, pwd, use_ssl = cfg
    M = imaplib.IMAP4_SSL(host) if use_ssl else imaplib.IMAP4(host)
    M.login(user, pwd); M.select("INBOX")
    typ, _ = M.uid('STORE', uid, '+FLAGS', r'(\Deleted)')
    if typ != 'OK':
        M.logout(); return False, "IMAP STORE failed"
    M.expunge(); M.logout()
    return True, None

def _imap_save_atts(uid: str):
    ok, cfg = _imap_cfg()
    if not ok:
        return False, "IMAP nicht konfiguriert"
    import imaplib, email, email.utils
    from email.header import decode_header, make_header
    from django.utils import timezone as tz

    host, user, pwd, use_ssl = cfg
    M = imaplib.IMAP4_SSL(host) if use_ssl else imaplib.IMAP4(host)
    M.login(user, pwd); M.select("INBOX")
    typ, data = M.uid("FETCH", uid, "(RFC822)")
    if typ != "OK" or not data or not data[0]:
        M.logout(); return False, "IMAP FETCH failed"

    raw = data[0][1]
    msg = email.message_from_bytes(raw)

    try:
        subject = str(make_header(decode_header(msg.get("Subject",""))))
    except Exception:
        subject = msg.get("Subject","")

    try:
        dt = email.utils.parsedate_to_datetime(msg.get("Date"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=tz.utc)
        date_part = dt.astimezone(tz.get_current_timezone()).strftime("%Y-%m-%d")
    except Exception:
        date_part = "unknown-date"

    base = _save_base() / date_part / _sanitize(subject or f"msg-{uid}")
    base.mkdir(parents=True, exist_ok=True)

    saved = []
    for part in msg.walk():
        if part.get_content_disposition() != "attachment":
            continue
        fname = part.get_filename() or "attachment.bin"
        try:
            fname = str(make_header(decode_header(fname)))
        except Exception:
            pass
        fname = _sanitize(fname)
        payload = part.get_payload(decode=True) or b""
        dest = base / fname
        stem, ext = os.path.splitext(fname); cnt = 1
        while dest.exists() and cnt < 1000:
            dest = base / f"{stem} ({cnt}){ext}"; cnt += 1
        with open(dest, "wb") as f:
            f.write(payload)
        saved.append(str(dest))

    M.logout()
    if not saved:
        return False, "Keine Datei-Anhänge gefunden."
    return True, f"Gespeichert in: {base}"

# --- Public Views ---
@login_required
def inbox_delete(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    msg_id = (request.POST.get("id") or "").strip()
    if not msg_id:
        return HttpResponseBadRequest("id fehlt")
    ok, err = _graph_delete(request.user, msg_id)
    if not ok:
        ok, err = _imap_delete(msg_id)
    if ok:
        messages.success(request, "E-Mail gelöscht.")
    else:
        messages.error(request, f"Löschen fehlgeschlagen: {err}")
    return redirect(request.META.get("HTTP_REFERER", "/crm/inbox/"))

@login_required
def inbox_save_attachments(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    msg_id = (request.POST.get("id") or "").strip()
    if not msg_id:
        return HttpResponseBadRequest("id fehlt")
    ok, info = _graph_save_atts(request.user, msg_id)
    if not ok:
        ok, info = _imap_save_atts(msg_id)
    if ok:
        messages.success(request, info)
    else:
        messages.error(request, f"Speichern fehlgeschlagen: {info}")
    return redirect(request.META.get("HTTP_REFERER", "/crm/inbox/"))
