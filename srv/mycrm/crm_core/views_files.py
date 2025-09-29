import re, shutil
from pathlib import Path
from urllib.parse import quote
from datetime import datetime, timezone as dt_timezone
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils import timezone
from django.template.loader import get_template

ROOT = Path(getattr(settings, "FILEMANAGER_ROOT", "/srv/mycrm/files")).resolve()

def _detect_base_template() -> str:
    candidates = [
        "crm_core/base.html",
        "base.html",
        "crm/base.html",
        "layout.html",
        "core/base.html",
    ]
    for name in candidates:
        try:
            get_template(name)
            return name
        except Exception:
            continue
    return "filemanager/_bare_base.html"

def _safe_join(rel: str) -> Path:
    rel = (rel or "").strip().lstrip("/")
    p = (ROOT / rel).resolve()
    if not str(p).startswith(str(ROOT)):
        raise Http404("Pfad außerhalb der Freigabe")
    return p

def _relpath(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(ROOT))
    except Exception:
        return ""

def _sanitize(name: str) -> str:
    name = re.sub(r'[\\/:*?"<>|]+', "_", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:180] if len(name) > 180 else name

def _unique_path(dst_dir: Path, filename: str) -> Path:
    filename = _sanitize(filename) or "unnamed"
    target = (dst_dir / filename)
    if not target.exists():
        return target
    stem = target.stem
    ext = target.suffix
    i = 2
    while True:
        cand = dst_dir / f"{stem} ({i}){ext}"
        if not cand.exists():
            return cand
        i += 1

@login_required
def index(request):
    rel = request.GET.get("p", "").strip()
    cur = _safe_join(rel)
    cur.mkdir(parents=True, exist_ok=True)

    entries = []
    try:
        items = sorted(cur.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except Exception:
        items = []
    for entry in items:
        st = entry.stat()
        dt_utc = datetime.fromtimestamp(st.st_mtime, tz=dt_timezone.utc)
        dt_local = timezone.localtime(dt_utc)
        entries.append({
            "name": entry.name,
            "is_dir": entry.is_dir(),
            "rel": _relpath(entry),
            "size": None if entry.is_dir() else st.st_size,
            "mtime": dt_local,
        })

    parent_rel = _relpath(cur.parent) if cur != ROOT else None
    return render(request, "filemanager/index.html", {
        "base_template": _detect_base_template(),
        "root": str(ROOT),
        "cur_rel": _relpath(cur),
        "parent_rel": parent_rel,
        "entries": entries,
    })

@login_required
def mkdir(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST erforderlich")

    rel  = request.POST.get("p", "").strip()
    name = (request.POST.get("name") or request.POST.get("folder") or request.POST.get("dirname") or request.GET.get("name") or "").strip()
    if not name:
        messages.error(request, "Name darf nicht leer sein.")
        return redirect(f"/crm/files/?p={quote(rel)}")

    name = _sanitize(name)
    if len(name) > 80:
        name = name[:80].rstrip()

    cur = _safe_join(rel)
    dest = _unique_path(cur, name)
    try:
        dest.mkdir()
        messages.success(request, f"Ordner angelegt: {dest.name}")
    except Exception as e:
        messages.error(request, f"Ordner konnte nicht angelegt werden: {e}")

    return redirect(f"/crm/files/?p={quote(rel)}")

@login_required
def upload(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST erforderlich")
    rel = request.POST.get("p", "").strip()
    cur = _safe_join(rel)
    files = request.FILES.getlist("files")
    if not files:
        messages.error(request, "Keine Datei ausgewählt.")
        return redirect(f"/crm/files/?p={quote(rel)}")
    saved, failed = 0, 0
    for f in files:
        try:
            dest = _unique_path(cur, f.name)
            with open(dest, "wb") as out:
                for chunk in f.chunks():
                    out.write(chunk)
            saved += 1
        except Exception as e:
            failed += 1
    if saved:
        messages.success(request, f"{saved} Datei(en) gespeichert in /{_relpath(cur)}.")
    if failed:
        messages.error(request, f"{failed} Datei(en) konnten nicht gespeichert werden.")
    return redirect(f"/crm/files/?p={quote(rel)}")

@login_required
def delete(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST erforderlich")
    target_rel = (request.POST.get("target") or "").strip().lstrip("/")
    if not target_rel:
        messages.error(request, "Ziel fehlt.")
        return redirect("/crm/files/")
    path = _safe_join(target_rel)
    parent_rel = _relpath(path.parent)
    try:
        if path.is_dir():
            force = request.POST.get("force") == "1"
            if force:
                shutil.rmtree(path)
            else:
                path.rmdir()
            messages.success(request, f"Ordner gelöscht: {path.name}")
        elif path.is_file():
            path.unlink()
            messages.success(request, f"Datei gelöscht: {path.name}")
        else:
            messages.error(request, "Ziel existiert nicht.")
    except Exception as e:
        messages.error(request, f"Löschen fehlgeschlagen: {e}")
    return redirect(f"/crm/files/?p={quote(parent_rel)}")
