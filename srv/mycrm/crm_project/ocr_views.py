"""Views rund um Anhang->Rechnung speichern (aus E-Mail)."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required

def _get_graph_token(request) -> Optional[str]:
    tok = request.session.get("graph_access_token")
    if tok:
        return tok
    try:
        from allauth.socialaccount.models import SocialToken
        st = (SocialToken.objects
              .filter(account__user=request.user, account__provider="microsoft")
              .first())
        if st and st.token:
            return st.token
    except Exception:
        pass
    return None

def _graph_get(url: str, token: str, is_bytes: bool = False):
    import requests
    hdr = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=hdr, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Graph {url} -> HTTP {r.status_code}")
    return r.content if is_bytes else r.json()

def _fetch_attachment_bytes_and_name(token: str, message_id: str, attachment_id: str):
    base = "https://graph.microsoft.com/v1.0/me"
    meta = _graph_get(f"{base}/messages/{message_id}/attachments/{attachment_id}", token, is_bytes=False)
    name = meta.get("name") or meta.get("id") or f"attachment_{attachment_id}"
    data = _graph_get(f"{base}/messages/{message_id}/attachments/{attachment_id}/$value", token, is_bytes=True)
    return name, data

def _pick_first_attachment_id(token: str, message_id: str) -> Optional[str]:
    """Falls keine attachment_id übergeben wurde: nimm PDF, sonst ersten Anhang."""
    base = "https://graph.microsoft.com/v1.0/me"
    js = _graph_get(f"{base}/messages/{message_id}/attachments?$select=id,name,contentType,size", token, is_bytes=False)
    items = (js or {}).get("value") or []
    if not items:
        return None
    # bevorzuge PDFs
    for it in items:
        ct = (it.get("contentType") or "").lower()
        nm = (it.get("name") or "").lower()
        if ct == "application/pdf" or nm.endswith(".pdf"):
            return it.get("id")
    # sonst erster
    return items[0].get("id")

def _save_into_filemanager(filename: str, data: bytes) -> str:
    root = "/srv/mycrm/var/files/invoices"
    os.makedirs(root, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = "".join(c for c in filename if c.isalnum() or c in (".","_","-")) or "attachment.bin"
    dst = os.path.join(root, f"{ts}_{safe}")
    with open(dst, "wb") as f:
        f.write(data)
    return dst

@login_required
@require_http_methods(["GET","POST"])
def attachments_save_invoice(request):
    """Speichert den gewählten (oder automatisch gewählten) E-Mail-Anhang im Datei-Manager."""
    mid = request.GET.get("message_id") or request.POST.get("message_id") \
        or request.GET.get("mid") or request.POST.get("mid")
    aid = request.GET.get("attachment_id") or request.POST.get("attachment_id") \
        or request.GET.get("aid") or request.POST.get("aid")
    if not mid:
        return HttpResponseBadRequest("message_id ist erforderlich.")

    try:
        token = _get_graph_token(request)
        if not token:
            return HttpResponseServerError("Kein Graph-Token gefunden (Session/Allauth).")

        if not aid:
            aid = _pick_first_attachment_id(token, mid)
            if not aid:
                return HttpResponseBadRequest("Kein Anhang bei dieser Nachricht gefunden.")

        name, data = _fetch_attachment_bytes_and_name(token, mid, aid)
        saved_path = _save_into_filemanager(name, data)

        return HttpResponse(
            f"<h3>Anhang gespeichert</h3>"
            f"<p><b>Datei:</b> {os.path.basename(saved_path)}</p>"
            f"<p><code>{saved_path}</code></p>"
            f"<p><a class='btn btn-primary' href='/crm/inbox/'>Zurück zur Mail</a></p>",
            content_type="text/html"
        )
    except Exception as e:
        return HttpResponseServerError(f"Speichern fehlgeschlagen: {e}")
