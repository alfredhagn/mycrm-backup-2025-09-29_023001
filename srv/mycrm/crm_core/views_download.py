import os, mimetypes, urllib.parse, logging
from pathlib import Path
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required

log = logging.getLogger(__name__)

BASE = Path(getattr(settings, "FILES_ROOT", "/srv/mycrm/files")).resolve()

def _safe_join(rel: str | None) -> Path:
    rel = (rel or "").strip()
    rel = rel.lstrip("/").replace("\\", "/")
    rel = urllib.parse.unquote(rel)
    parts = [p for p in rel.split("/") if p not in ("", ".", "..") and p != ""]
    path = BASE.joinpath(*parts) if parts else BASE
    # innerhalb BASE bleiben
    try:
        path.resolve().relative_to(BASE)
    except Exception:
        raise Http404("invalid path")
    return path

def _fallback_find(dirpath: Path, name: str) -> Path | None:
    cand = dirpath / name
    if cand.exists() and cand.is_file():
        return cand
    low = name.casefold()
    try:
        for ch in dirpath.iterdir():
            if ch.is_file() and ch.name.casefold() == low:
                return ch
    except FileNotFoundError:
        return None
    return None

def _search_any(name: str, max_hits: int = 2) -> list[Path]:
    """Wenn p fehlt/falsch: nach exakt gleichem Dateinamen unterhalb BASE suchen."""
    low = name.casefold()
    hits: list[Path] = []
    for root, _, files in os.walk(BASE):
        for fn in files:
            if fn.casefold() == low:
                hits.append(Path(root) / fn)
                if len(hits) >= max_hits:
                    return hits
    return hits

def _open_response(path: Path, inline: bool):
    ctype = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    resp = FileResponse(open(path, "rb"), content_type=ctype)
    disp = "inline" if inline else "attachment"
    resp["Content-Disposition"] = f"{disp}; filename*=UTF-8''" + urllib.parse.quote(path.name)
    return resp

@login_required
def view_file(request):
    rel = request.GET.get("p", "") or ""
    raw_name = request.GET.get("name")
    if not raw_name:
        return HttpResponseBadRequest("missing name")
    name = urllib.parse.unquote(raw_name).replace("\\", "/").split("/")[-1]

    dirpath = _safe_join(rel)
    path = _fallback_find(dirpath, name)

    # Fallback: p leer/ungültig -> rekursiv nach Name suchen
    if not path:
        hits = _search_any(name, max_hits=3)
        log.info("files.view_file fallback: rel=%r name=%r hits=%s", rel, name, [str(h) for h in hits])
        if len(hits) == 1:
            path = hits[0]
        elif len(hits) > 1:
            raise Http404("multiple matches for filename; specify p")
        else:
            raise Http404("file not found")

    return _open_response(path, inline=True)

@login_required
def download_file(request):
    rel = request.GET.get("p", "") or ""
    raw_name = request.GET.get("name")
    if not raw_name:
        return HttpResponseBadRequest("missing name")
    name = urllib.parse.unquote(raw_name).replace("\\", "/").split("/")[-1]

    dirpath = _safe_join(rel)
    path = _fallback_find(dirpath, name)

    if not path:
        hits = _search_any(name, max_hits=3)
        log.info("files.download_file fallback: rel=%r name=%r hits=%s", rel, name, [str(h) for h in hits])
        if len(hits) == 1:
            path = hits[0]
        elif len(hits) > 1:
            raise Http404("multiple matches for filename; specify p")
        else:
            raise Http404("file not found")

    return _open_response(path, inline=False)
