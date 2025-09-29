#!/bin/sed -f

# Ergänze Importe
0,/^from /s|^from .models import Message$|from .models import Message\nfrom .models_expenses import ExpenseDraft\nfrom .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer\nfrom django.http import HttpResponseBadRequest\nfrom django.shortcuts import redirect\nimport logging\nlogger = logging.getLogger(__name__)|

# Füge neue View am Ende ein
$ a\
\ndef ocr_from_email(request):\
    """OCR-E-Mail-PDF und lege Vormerkung an."""\
    mid = request.GET.get("message_id")\
    if not mid:\
        return HttpResponseBadRequest("message_id fehlt")\
\
    logger.info("OCR gestartet für message_id=%s", mid)\
\
    from .ms_graph_helpers import list_attachments, fetch_attachment_bytes\
    from .ms_tokens import get_ms_session\
\
    sess = get_ms_session(request)\
    if not sess:\
        logger.error("Kein MS-Session-Token verfügbar")\
        return HttpResponseBadRequest("Kein Graph-Token")\
\
    atts = list_attachments(sess, mid)\
    pick = next((a for a in atts if str(a.get("contentType", "")).lower() == "application/pdf"), None)\
    if not pick:\
        return HttpResponseBadRequest("Kein PDF-Anhang gefunden")\
\
    data = fetch_attachment_bytes(sess, mid, pick["id"])\
    text = extract_text(data)\
\
    net, vat, gross, rate = find_amounts(text)\
    inv_date = find_invoice_date(text)\
    issuer = find_issuer(text, "")\
\
    d = ExpenseDraft()\
    if inv_date: d.date = inv_date\
    if gross: d.amount = gross\
    if issuer: d.supplier = issuer\
    d.message_id = mid\
    d.description = "OCR-Erkennung"\
    if issuer: d.description += f" – {issuer}"\
    if gross: d.description += f" – {gross} EUR"\
    d.save()\
\
    logger.info("OCR-Vormerkung gespeichert für message_id=%s", mid)\
    return redirect("/crm/expenses/drafts/")
