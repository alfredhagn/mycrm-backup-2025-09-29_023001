#!/bin/sed -f

# Füge Importblöcke ein (nur wenn nicht vorhanden)
0,/^from /s|^from .models import Message$|from .models import Message\nfrom .models_expenses import ExpenseDraft\nfrom . import ocr_invoice\nfrom django.http import HttpResponseBadRequest\nfrom django.shortcuts import redirect|

# Füge neue Funktion am Ende der Datei hinzu
$ a\
\ndef draft_from_email_bridge(request):\
    """\
    Öffnet E-Mail, extrahiert PDF, führt OCR durch, erstellt Vormerkung.\
    """\
    mid = request.GET.get("message_id")\
    if not mid:\
        return HttpResponseBadRequest("message_id fehlt")\
\
    msg = Message.objects.get(id=mid)\
\
    if not msg.attachments.exists():\
        return HttpResponseBadRequest("keine Anhänge gefunden")\
\
    fileobj = msg.attachments.first().get_file()\
    data = ocr_invoice.extract_invoice_data(fileobj)\
\
    ExpenseDraft.objects.create(\
        amount=data.amount,\
        description=data.description,\
        supplier=data.supplier,\
        category=data.category,\
        date=data.date,\
        source="email",\
        message_id=mid\
    )\
\
    return redirect("/crm/expenses/drafts/")
