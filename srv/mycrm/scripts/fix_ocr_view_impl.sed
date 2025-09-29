#!/bin/sed -f
$ a\

def ocr_from_email(request):\
    from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseServerError\
    from django.shortcuts import redirect\
    from .models import Message\
    from .models_expenses import ExpenseDraft\
    try:\
        from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer\
    except Exception as e:\
        return HttpResponseServerError("OCR-Modul fehlt: %s" % e)\
    import logging\
    logger = logging.getLogger(__name__)\
    mid = request.GET.get("message_id") or request.GET.get("mid")\
    if not mid:\
        return HttpResponseBadRequest("message_id fehlt")\
    try:\
        sess = get_ms_session(request)\
        if not sess:\
            return HttpResponseBadRequest("Kein Graph-Token")\
        aid = request.GET.get("aid")\
        atts = list_attachments(sess, mid)\
        pick = None\
        if aid:\
            pick = next((a for a in atts if a.get("id")==aid), None)\
        if pick is None:\
            pick = next((a for a in atts if str(a.get("contentType","")).lower()=="application/pdf"), None)\
        if pick is None:\
            return HttpResponseBadRequest("Kein PDF-Anhang gefunden")\
        data = fetch_attachment_bytes(sess, mid, pick["id"])\
        text = extract_text(data)\
        net, vat, gross, rate = find_amounts(text)\
        inv_date = find_invoice_date(text)\
        issuer = find_issuer(text, "")\
        payload = {"mid": mid, "aid": pick.get("id"), "issuer": issuer, "date": (inv_date.isoformat() if hasattr(inv_date, "isoformat") else inv_date), "amount": (str(gross) if gross is not None else None)}\
        if request.GET.get("debug"):\
            return JsonResponse(payload)\
        d = ExpenseDraft()\
        if inv_date: d.date = inv_date\
        if gross is not None: d.amount = gross\
        if issuer: d.supplier = issuer\
        d.message_id = mid\
        d.description = "OCR-Erkennung" + (f" – {issuer}" if issuer else "") + (f" – {gross} EUR" if gross is not None else "")\
        d.save()\
        logger.info("OCR-Vormerkung gespeichert: mid=%s aid=%s amount=%s", mid, pick.get("id"), gross)\
        return redirect("/crm/expenses/drafts/")\
    except Exception as e:\
        logger.exception("OCR-Fehler: %s", e)\
        return HttpResponseServerError("OCR-Fehler")
