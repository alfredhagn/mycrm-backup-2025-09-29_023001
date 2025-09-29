
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import logging, importlib
from pathlib import Path
from .ocr_invoice import extract_text, parse_invoice_text

logger = logging.getLogger(__name__)

def _resolve_attachment(pk):
    candidates = [
        ("crm_mail.models", "EmailAttachment"),
        ("mail.models", "EmailAttachment"),
        ("crm_core.models", "EmailAttachment"),
        ("crm_core.models", "Attachment"),
    ]
    for mod, cls in candidates:
        try:
            m = importlib.import_module(mod)
            C = getattr(m, cls, None)
            if C is None: continue
            obj = C.objects.filter(pk=pk).first()
            if obj:
                # mögliche Feldnamen
                for f in ("file","document","attachment","content","blob"):
                    if hasattr(obj, f):
                        filefield = getattr(obj, f)
                        path = getattr(filefield, "path", None) or getattr(filefield, "name", None)
                        ctype = getattr(filefield, "content_type", None) or getattr(obj, "content_type", None)
                        if path:
                            return str(path), ctype, obj
        except Exception as ex:
            logger.warning("OCR resolve failed for %s.%s: %s", mod, cls, ex)
    return None, None, None

@login_required
def attachment_ocr(request, pk: int):
    path, ctype, obj = _resolve_attachment(pk)
    if not path:
        return JsonResponse({"ok": False, "error": "attachment_not_found", "id": pk}, status=404)
    try:
        txt = extract_text(path, ctype)
        data = parse_invoice_text(txt, source_path=path)
        if request.GET.get("format") == "html":
            ctx = {"attachment": obj, "ocr": data, "text": txt}
            # optionales Template (falls vorhanden); sonst Fallback
            try:
                return render(request, "ocr/preview.html", ctx)
            except Exception:
                html = "<h3>OCR-Vorschau</h3><pre style='white-space:pre-wrap'>%s</pre><hr><pre>%s</pre>" % (data, txt[:5000])
                return HttpResponse(html)
        return JsonResponse({"ok": True, "id": pk, "data": data})
    except Exception as ex:
        logger.exception("OCR failed for attachment %s: %s", pk, ex)
        return JsonResponse({"ok": False, "error": "ocr_failed", "id": pk, "detail": str(ex)}, status=500)
