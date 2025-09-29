import io, urllib.parse, requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, FileResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings

ROOT_ONEDRIVE = getattr(settings, "MYCRM_ONEDRIVE_ROOT", "MyCRM")

def _ensure_onedrive_root(token, root_name=None):
    root_name = root_name or ROOT_ONEDRIVE
    import urllib.parse, requests, json
    # Existenz prüfen (Metadaten des Zielordners anfragen)
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(root_name, safe='')}"
    r = requests.get(url, headers=_graph_headers(token), timeout=20)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        # Anlegen unterhalb von /root
        headers = _graph_headers(token).copy()
        headers["Content-Type"] = "application/json"
        payload = {"name": root_name, "folder": {}, "@microsoft.graph.conflictBehavior": "fail"}
        r2 = requests.post(
            "https://graph.microsoft.com/v1.0/me/drive/root/children",
            headers=headers,
            data=json.dumps(payload),
            timeout=20,
        )
        return r2.status_code in (200, 201, 409)
    return False
from django.views.decorators.http import require_http_methods

# Wenn du die Helfer schon hast, gerne centralisieren. Hier lokal rein:
def _graph_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def _graph_token_for(user):
    try:
        from allauth.socialaccount.models import SocialToken
    except Exception:
        return None
    try:
        tok = (SocialToken.objects
               .filter(account__user=user, app__provider="microsoft")
               .order_by("-id").first())
        return tok.token if tok else None
    except Exception:
        return None

def _ensure_token(request):
    token = _graph_token_for(request.user)
    try:
        _ensure_onedrive_root(token, ROOT_ONEDRIVE)
    except Exception:
        pass
    if not token:
        messages.error(request, "Kein Microsoft-Token – bitte neu verbinden.")
        return None
    return token

@login_required
def onedrive_browser(request):
    token = _ensure_token(request)
    if not token:
        return redirect("/crm/")

    path = (request.GET.get("path") or "").strip().strip("/")
    if path:
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(path, safe='/')}:/children"
    else:
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"

    r = requests.get(url, headers=_graph_headers(token), timeout=20)
    if r.status_code != 200:
        messages.error(request, f"Graph {r.status_code}: {r.text[:200]}")
        return redirect("/crm/")

    items = r.json().get("value", [])

    # Breadcrumbs
    crumbs = []
    accum = ""
    for part in (path.split("/") if path else []):
        accum = f"{accum}/{part}" if accum else part
        crumbs.append((part, accum))

    return render(request, "onedrive/browser.html", {
        "items": items,
        "path": path,
        "crumbs": crumbs,
    })

@login_required
@require_http_methods(["POST"])
def onedrive_mkdir(request):
    token = _ensure_token(request)
    if not token:
        return redirect("onedrive_browser")

    path = (request.POST.get("path") or "").strip().strip("/")
    name = (request.POST.get("name") or "").strip()
    if not name:
        return HttpResponseBadRequest("name fehlt")

    parent = f"/{path}" if path else ""
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(parent, safe='/')}:/children"
    payload = {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "rename"}

    r = requests.post(url, json=payload, headers=_graph_headers(token), timeout=20)
    if r.status_code not in (200, 201):
        messages.error(request, f"Ordner anlegen fehlgeschlagen ({r.status_code}).")
    else:
        messages.success(request, f"Ordner „{name}“ erstellt.")

    return redirect(f"{reverse('onedrive_browser')}?path={urllib.parse.quote(path, safe='/')}")

@login_required
@require_http_methods(["POST"])
def onedrive_upload(request):
    token = _ensure_token(request)
    if not token:
        return redirect("onedrive_browser")

    path = (request.POST.get("path") or "").strip().strip("/")
    up = request.FILES.get("file")
    if not up:
        return HttpResponseBadRequest("file fehlt")

    name = up.name
    parent = f"/{path}" if path else ""
    graph_path = parent + ("/" if parent and not parent.endswith("/") else "") + name
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(graph_path, safe='/')}:/content"

    # Small upload (<=4 MB). Für größere Dateien später Upload Session nutzen.
    r = requests.put(url, data=up.read(), headers=_graph_headers(token), timeout=60)
    if r.status_code not in (200, 201):
        messages.error(request, f"Hochladen fehlgeschlagen ({r.status_code}).")
    else:
        messages.success(request, f"„{name}“ hochgeladen.")

    return redirect(f"{reverse('onedrive_browser')}?path={urllib.parse.quote(path, safe='/')}")

@login_required
def onedrive_download(request, item_id: str):
    token = _ensure_token(request)
    if not token:
        return redirect("onedrive_browser")

    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/content"
    r = requests.get(url, headers=_graph_headers(token), stream=True, timeout=60)
    if r.status_code != 200:
        messages.error(request, f"Download fehlgeschlagen ({r.status_code}).")
        return redirect("onedrive_browser")

    # Dateiname aus Header ist optional – FileResponse kümmert sich um Streaming
    return FileResponse(r.raw, as_attachment=True)

@login_required
def onedrive_share(request, item_id: str):
    token = _ensure_token(request)
    if not token:
        return redirect("onedrive_browser")

    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{item_id}/createLink"
    r = requests.post(url, json={"type": "view", "scope": "anonymous"},
                      headers=_graph_headers(token), timeout=20)
    if r.status_code not in (200, 201):
        messages.error(request, f"Freigabelink fehlgeschlagen ({r.status_code}).")
        return redirect("onedrive_browser")

    web_url = (r.json().get("link") or {}).get("webUrl")
    if web_url:
        messages.success(request, f"Freigabelink: {web_url}")
    return redirect("onedrive_browser")
