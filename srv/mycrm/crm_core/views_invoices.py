from django.urls import reverse, NoReverseMatch
from django.db import models
from django.apps import apps
from django.contrib import messages
from django.urls import NoReverseMatch
from .ms_graph_helpers import list_attachments, fetch_attachment_bytes
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.base import ContentFile
from django.http import HttpResponseBadRequest
from django.db import transaction
from .models_invoices import InvoiceDraft
from .invoice_extract import extract_text, find_amounts, find_invoice_number, find_invoice_date, find_issuer, sha256, guess_currency

import base64, requests

def _get_ms_session(request):
    try:
        from .ms_tokens import get_ms_session  # type: ignore
        return get_ms_session(request)
    except Exception:
        return None

def _fetch_pdf_from_graph(sess, msg_id: str, att_id: str) -> bytes|None:
    # /me/messages/{id}/attachments/{id}/$value liefert raw bytes bei fileAttachment
    url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}/attachments/{att_id}/$value"
    try:
        if hasattr(sess, "get"):
            r = sess.get(url, timeout=20)
            r.raise_for_status()
            return r.content
    except Exception:
        return None
    return None

@login_required
@require_http_methods(["GET"])
def draft_from_email(request):

    """
    Create/Update an ExpenseDraft from an email attachment or direct download.
    GET: (download) ODER (mid & aid). Redirects to /crm/expenses/drafts/
    """
    from django.http import HttpResponseBadRequest
    from django.contrib import messages
    from django.utils import timezone
    from django.shortcuts import redirect
    import requests

    download = request.GET.get("download")
    mid      = request.GET.get("mid")
    aid      = request.GET.get("aid")
    if not (download or (mid and aid)):
        return HttpResponseBadRequest("Erwarte (download) oder (mid & aid).")

    # ggf. Graph-Session
    sess = None
    if mid and aid:
        token = request.session.get("ms_access_token") or request.session.get("ms_token")
        if token:
            sess = requests.Session()
            sess.headers["Authorization"] = f"Bearer {token}"
            sess.headers["Accept"] = "application/json"

    # PDF holen
    pdf_bytes = None
    print(f"draft_from_email: mid={mid} aid={aid} download={'yes' if download else 'no'}")
    try:
        if download:
            r = requests.get(download, timeout=30)
            r.raise_for_status()
            pdf_bytes = r.content
        elif sess is not None:
            from .ms_graph_helpers import fetch_attachment_bytes
            pdf_bytes = fetch_attachment_bytes(sess, mid, aid)
    except Exception as e:
        messages.warning(request, f"PDF-Download fehlgeschlagen: {e}")

    # ExpenseDraft laden/erzeugen (per message_id wenn vorhanden)
    ExpenseDraft = apps.get_model("crm_core","ExpenseDraft")
    exp = ExpenseDraft.objects.filter(message_id=mid).order_by("-id").first() if mid else None
    if exp is None:
        exp = ExpenseDraft()

    # Basisdaten
    try:
        if mid and hasattr(exp,"message_id"):
            exp.message_id = mid
    except Exception: pass
    try:
        if hasattr(exp,'date') and not getattr(exp,'date', None):
            exp.date = timezone.localdate()
    except Exception: pass
    try:
        # Falls der Aufrufer den Mail-Betreff als subject übergibt
        subj = request.GET.get("subject") or ""
        if subj and hasattr(exp,'description') and not getattr(exp,'description',''):
            exp.description = subj[:200]
    except Exception: pass

    # Anreichern aus PDF
    if pdf_bytes:
        print(f"draft_from_email: got PDF bytes len={0 if pdf_bytes is None else len(pdf_bytes)}")

        _populate_expense_from_pdf_bytes(exp, pdf_bytes)
        print(f"extracted -> amount={getattr(exp,'amount',None)} supplier={getattr(exp,'supplier',None)!r} date={getattr(exp,'date',None)}")

    # Speichern
    try:
        exp.save()
        messages.success(request, f"Ausgabe-Entwurf #{exp.pk} aktualisiert.")
    except Exception as e:
        messages.error(request, f"Speichern fehlgeschlagen: {e}")

    return redirect("/crm/expenses/drafts/")

def draft_detail(request, pk: int):
    d = get_object_or_404(InvoiceDraft, pk=pk)
    return render(request, "invoices/draft_detail.html", {"d": d})

@login_required
@require_http_methods(["POST"])
@transaction.atomic
def draft_save(request):
    pk = request.POST.get("pk")
    d = get_object_or_404(InvoiceDraft, pk=pk)
    # Form-Felder übernehmen (server-seitig validierbar, hier minimal)
    d.issuer = request.POST.get("issuer","")[:255]
    d.invoice_number = request.POST.get("invoice_number","")[:128]
    d.currency = request.POST.get("currency","EUR")[:8]
    for fld in ("net_amount","vat_amount","gross_amount","vat_rate"):
        val = request.POST.get(fld)
        try:
            d.__dict__[fld] = None if val in (None,"") else float(val.replace(",","."))  # pragmatisch
        except Exception:
            pass
    d.status = "draft"  # später: "ready" wenn validiert
    d.save()
    return redirect("inv_draft_detail", pk=d.pk)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models_invoices import InvoiceDraft

@login_required
def drafts_list(request):
    rows = InvoiceDraft.objects.order_by('-created_at')[:100]
    return render(request, "invoices/drafts_list.html", {"rows": rows})


from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer

def _populate_from_pdf_bytes(draft, pdf_bytes: bytes):
    text = extract_text(pdf_bytes)
    net, vat, gross, rate = find_amounts(text)
    # ExpenseDraft: Betrag befüllen (amount = gross oder net+vat)
    try:
        if hasattr(draft, 'amount'):
            if gross is not None:
                draft.amount = gross
            elif net is not None and vat is not None:
                draft.amount = (net + vat)
    except Exception:
        pass
    if hasattr(draft, "net_amount")   and net   is not None: draft.net_amount = net
    if hasattr(draft, "gross_amount") and gross is not None: draft.gross_amount = gross
    if hasattr(draft, "vat_amount"):
        draft.vat_amount = vat if vat is not None else ((gross - net) if (gross is not None and net is not None) else None)
    if hasattr(draft, "vat_rate"):
        draft.vat_rate = rate if (rate is not None) else ((draft.vat_amount / draft.net_amount * 100) if getattr(draft,'net_amount',0) else None)
    if hasattr(draft, "invoice_date"):
        inv_date = find_invoice_date(text)
        if inv_date: draft.invoice_date = inv_date
    if hasattr(draft, "issuer"):
        issuer = find_issuer(text, getattr(draft,'issuer', '') or '')
        if issuer: draft.issuer = issuer
    if hasattr(draft, "raw_text"):
        draft.raw_text = text[:20000]


import logging, requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.db.models.fields.files import FileField
from .models_invoices import InvoiceDraft
from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer

log = logging.getLogger("crm.invoices")

def _first_filefield_name(obj):
    for f in obj._meta.fields:
        if isinstance(f, FileField):
            return f.name
    return None

def _attach_pdf(draft, pdf_bytes: bytes, filename: str="import.pdf"):
    name = _first_filefield_name(draft) or "pdf_file"
    if hasattr(draft, name):
        getattr(draft, name).save(filename, ContentFile(pdf_bytes), save=False)

@login_required
def draft_import_url(request):
    url = request.GET.get("url")
    if not url:
        return HttpResponseBadRequest("url parameter required")
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        pdf_bytes = r.content
    except Exception as e:
        log.exception("download failed")
        return HttpResponseBadRequest("download failed")

    d = InvoiceDraft()
    # minimale Defaults, falls Felder existieren
    for name, val in [("status","draft")]:
        if hasattr(d, name):
            setattr(d, name, val)
    d.save()
    _attach_pdf(d, pdf_bytes, filename=url.split("/")[-1] or "import.pdf")

    # Felder aus PDF befüllen (OCR-Fallback ist in invoice_extract enthalten)
    text = extract_text(pdf_bytes)
    net, vat, gross, rate = find_amounts(text)
    issuer = find_issuer(text, getattr(d,"issuer",""))
    inv_date = find_invoice_date(text)

    def setif(attr, val):
        if hasattr(d, attr) and val is not None:
            setattr(d, attr, val)

    setif("net_amount", net)
    setif("gross_amount", gross)
    setif("vat_amount", vat if vat is not None else ((gross - net) if (gross is not None and net is not None) else None))
    setif("vat_rate", rate if rate is not None else ((getattr(d,"vat_amount",0) / getattr(d,"net_amount",1) * 100) if getattr(d,"net_amount",0) else None))
    setif("invoice_date", inv_date)
    setif("issuer", issuer)
    if hasattr(d, "raw_text"): d.raw_text = text[:20000]
    d.save()

    try:
        from django.urls import reverse
        return redirect(reverse("inv_draft_detail", args=[d.pk]))
    except Exception:
        return redirect("/crm/invoices/drafts/")



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from .models_invoices import InvoiceDraft
from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer

@login_required
def draft_upload(request):
    if request.method == 'POST':
        f = request.FILES.get('pdf')
        if not f:
            return HttpResponseBadRequest('Bitte PDF hochladen.')
        pdf_bytes = f.read()
        d = InvoiceDraft()
        if hasattr(d, 'status'): d.status = 'draft'
        d.save()
        _attach_pdf(d, pdf_bytes, filename=f.name)

        text = extract_text(pdf_bytes)  # nutzt pypdf -> pdfminer -> OCR (falls nötig)
        net, vat, gross, rate = find_amounts(text)
        issuer = find_issuer(text, getattr(d,'issuer','') or f.name)
        inv_date = find_invoice_date(text)

        def setif(attr, val):
            if hasattr(d, attr) and val is not None:
                setattr(d, attr, val)

        setif('net_amount', net)
        setif('gross_amount', gross)
        setif('vat_amount', vat if vat is not None else ((gross - net) if (gross is not None and net is not None) else None))
        setif('vat_rate', rate if rate is not None else ((getattr(d,'vat_amount',0) / getattr(d,'net_amount',1) * 100) if getattr(d,'net_amount',0) else None))
        setif('invoice_date', inv_date)
        setif('issuer', issuer)
        if hasattr(d,'raw_text'): d.raw_text = text[:20000]
        d.save()

        try:
            from django.urls import reverse
            return redirect(reverse('inv_draft_detail', args=[d.pk]))
        except Exception:
            return redirect('/crm/invoices/drafts/')
    return render(request, 'invoices/draft_upload.html')



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from .models_invoices import InvoiceDraft
from .ms_tokens import get_ms_session
from .ms_graph_helpers import list_attachments, fetch_attachment_bytes
import requests
from django.core.files.base import ContentFile
from decimal import Decimal

def _first_filefield_name(obj):
    from django.db.models.fields.files import FileField as _FF
    for f in obj._meta.fields:
        if isinstance(f, _FF):
            return f.name
    return None

def _attach_pdf(draft, pdf_bytes: bytes, filename: str='mail.pdf'):
    name = _first_filefield_name(draft) or 'pdf'
    if hasattr(draft, name):
        getattr(draft, name).save(filename, ContentFile(pdf_bytes), save=False)

from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer
def _populate_from_pdf_bytes(draft, pdf_bytes: bytes):
    text = extract_text(pdf_bytes)
    net, vat, gross, rate = find_amounts(text)
    if hasattr(draft,'net_amount')   and net   is not None: draft.net_amount   = net
    if hasattr(draft,'gross_amount') and gross is not None: draft.gross_amount = gross
    if hasattr(draft,'vat_amount'):
        draft.vat_amount = vat if vat is not None else ((gross - net) if (gross is not None and net is not None) else None)
    if hasattr(draft,'vat_rate') and rate is not None:
        try:
            draft.vat_rate = rate.quantize(Decimal('1')) if isinstance(rate, Decimal) else rate
        except Exception:
            draft.vat_rate = rate
    if hasattr(draft,'invoice_date'):
        d = find_invoice_date(text)
        if d: draft.invoice_date = d
    if hasattr(draft,'issuer'):
        iss = find_issuer(text, getattr(draft,'issuer',''))
        if iss: draft.issuer = iss
    if hasattr(draft,'raw_text'):
        draft.raw_text = text[:20000]

@login_required
def draft_from_email(request):
    mid = request.GET.get("mid")
    aid = request.GET.get("aid")
    download = request.GET.get("download")
    next_url = request.GET.get("next")

    pdf_bytes = None
    filename = "mail.pdf"

    if download:
        try:
            r = requests.get(download, timeout=30)
            if r.status_code >= 400 or not r.content:
                return HttpResponseBadRequest("Download fehlgeschlagen.")
            pdf_bytes = r.content
            try:
                from urllib.parse import urlparse
                fn = urlparse(download).path.rsplit("/",1)[-1]
                if fn: filename = fn
            except Exception:
                pass
        except Exception:
            return HttpResponseBadRequest("Download fehlgeschlagen (Netzwerk).")
    elif mid:
        sess = get_ms_session(request)
        if not sess:
            return HttpResponseBadRequest("Kein MS-Session-Token verfügbar.")
        try:
            atts = list_attachments(sess, mid)
        except Exception:
            return HttpResponseBadRequest("Anhänge konnten nicht geladen werden.")
        pick = None
        if aid:
            pick = next((a for a in atts if a.get("id")==aid), None)
            if not pick:
                return HttpResponseBadRequest("Attachment nicht gefunden.")
        else:
            pdfs = [a for a in atts if str(a.get("contentType","")).lower().startswith("application/pdf") or str(a.get("name","")).lower().endswith(".pdf")]
            if not pdfs:
                return HttpResponseBadRequest("Kein PDF-Anhang gefunden.")
            pick = pdfs[0]
        try:
            pdf_bytes = fetch_attachment_bytes(sess, mid, pick["id"])
        except Exception:
            return HttpResponseBadRequest("Attachment-Download fehlgeschlagen.")
        filename = pick.get("name") or filename
    else:
        return HttpResponseBadRequest("Erwarte (?mid[&aid]) oder (?download=URL).")

    d = InvoiceDraft()
    if hasattr(d, "status"):
        try: d.status = "draft"
        except Exception: pass
    if hasattr(d, "created_by") and getattr(request, "user", None) and request.user.is_authenticated:
        d.created_by = request.user
    d.save()

    _attach_pdf(d, pdf_bytes, filename=filename or "mail.pdf")
    _populate_from_pdf_bytes(d, pdf_bytes)
    d.save()

    messages.success(request, "Rechnung als Entwurf vorgemerkt.")

    if next_url:
        return redirect(next_url)

    # bevorzugte Detail-URL-Namen (expenses-first), dann Fallback auf Liste
    for name in ("exp_draft_detail","expenses_draft_detail","expense_draft_detail",
                 "inv_draft_detail","draft_detail"):
        try:
            return redirect(reverse(name, args=[d.pk]))
        except NoReverseMatch:
            continue

    return redirect("/crm/expenses/drafts/")  # <- dein gewünschter Listing-Pfad


def _set_first(obj, names, value):
    if value is None:
        return False
    for n in names:
        if hasattr(obj, n):
            setattr(obj, n, value)
            return True
    return False

from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer

def _populate_generic_from_pdf(draft, pdf_bytes: bytes):
    text = extract_text(pdf_bytes)
    net, vat, gross, rate = find_amounts(text)
    # Rate als ganze Zahl
    try:
        if isinstance(rate, Decimal):
            rate = rate.quantize(Decimal('1'))
    except Exception:
        pass

    _set_first(draft, ['gross_amount','amount_brutto','brutto','total','amount_total'], gross)
    _set_first(draft, ['net_amount','amount_netto','net','subtotal'], net)
    # VAT-Betrag – falls nicht direkt, aus g-n
    if vat is None and (gross is not None and net is not None):
        vat = (gross - net)
    _set_first(draft, ['vat_amount','tax_amount','mwst_betrag','ust_betrag'], vat)
    _set_first(draft, ['vat_rate','tax_rate','mwst_satz','ust_satz'], rate)

    inv_date = find_invoice_date(text)
    _set_first(draft, ['invoice_date','date','document_date','doc_date'], inv_date)

    issuer = find_issuer(text, getattr(draft,'issuer', '') or '')
    _set_first(draft, ['issuer','vendor','supplier','creditor','payee'], issuer)
    # Beschreibung auffüllen, falls leer
    try:
        desc_empty = (not getattr(draft, 'description', ''))
    except Exception:
        desc_empty = False
    if desc_empty and hasattr(draft, 'description'):
        parts = []
        try:
            if issuer: parts.append(str(issuer))
        except Exception: pass
        try:
            if inv_date: parts.append(str(inv_date))
        except Exception: pass
        try:
            if gross is not None: parts.append(f"{gross} EUR")
        except Exception: pass
        draft.description = " – ".join([p for p in parts if p]) or "Rechnung"
    # Beschreibung auffüllen, falls leer
    try:
        desc_empty = (not getattr(draft, 'description', ''))
    except Exception:
        desc_empty = False
    if desc_empty and hasattr(draft, 'description'):
        parts = []
        try:
            if issuer: parts.append(str(issuer))
        except Exception: pass
        try:
            if inv_date: parts.append(str(inv_date))
        except Exception: pass
        try:
            if gross is not None: parts.append(f"{gross} EUR")
        except Exception: pass
        draft.description = " – ".join([p for p in parts if p]) or "Rechnung"



    if hasattr(draft, 'raw_text'):
        draft.raw_text = text[:20000]

def _get_draft_model():
    # bevorzugte Kandidaten
    candidates = [
        ('crm_core','ExpenseDraft'),
        ('crm_core','InvoiceDraft'),
        ('expenses','ExpenseDraft'),
        ('invoices','InvoiceDraft'),
    ]
    for app_label, model_name in candidates:
        try:
            m = apps.get_model(app_label, model_name)
            if m is not None:
                return m
        except Exception:
            pass
    # Fallback
    try:
        from .models_invoices import InvoiceDraft
        return InvoiceDraft
    except Exception:
        return None



from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest
from .ms_tokens import get_ms_session
from .ms_graph_helpers import list_attachments, fetch_attachment_bytes

@login_required
def draft_from_email(request):
    mid = request.GET.get("mid")
    aid = request.GET.get("aid")
    download = request.GET.get("download")
    next_url = request.GET.get("next")

    pdf_bytes = None
    filename = "mail.pdf"

    if download:
        try:
            r = requests.get(download, timeout=30)
            if r.status_code >= 400 or not r.content:
                return HttpResponseBadRequest("Download fehlgeschlagen.")
            pdf_bytes = r.content
            try:
                from urllib.parse import urlparse
                fn = urlparse(download).path.rsplit("/",1)[-1]
                if fn: filename = fn
            except Exception:
                pass
        except Exception:
            return HttpResponseBadRequest("Download fehlgeschlagen (Netzwerk).")
    elif mid:
        sess = get_ms_session(request)
        if not sess:
            return HttpResponseBadRequest("Kein MS-Session-Token verfügbar.")
        try:
            atts = list_attachments(sess, mid)
        except Exception:
            return HttpResponseBadRequest("Anhänge konnten nicht geladen werden.")
        pick = None
        if aid:
            pick = next((a for a in atts if a.get("id")==aid), None)
            if not pick:
                return HttpResponseBadRequest("Attachment nicht gefunden.")
        else:
            pdfs = [a for a in atts if str(a.get("contentType","")).lower().startswith("application/pdf") or str(a.get("name","")).lower().endswith(".pdf")]
            if not pdfs:
                return HttpResponseBadRequest("Kein PDF-Anhang gefunden.")
            pick = pdfs[0]
        try:
            pdf_bytes = fetch_attachment_bytes(sess, mid, pick["id"])
        except Exception:
            return HttpResponseBadRequest("Attachment-Download fehlgeschlagen.")
        filename = pick.get("name") or filename
    else:
        return HttpResponseBadRequest("Erwarte (?mid[&aid]) oder (?download=URL).")

    DraftModel = _get_draft_model()
    if DraftModel is None:
        return HttpResponseBadRequest("Draft-Modell nicht gefunden.")

    d = DraftModel()
    # sinnvolle Defaults
    if hasattr(d, "status"):
        try: d.status = "draft"
        except Exception: pass
    if hasattr(d, "created_by") and getattr(request, "user", None) and request.user.is_authenticated:
        d.created_by = request.user
    d.save()

    # Datei anhängen + Felder setzen
    _attach_pdf(d, pdf_bytes, filename=filename or "mail.pdf")
    _populate_generic_from_pdf(d, pdf_bytes)
    d.save()

    messages.success(request, "Rechnung als Entwurf vorgemerkt.")

    if next_url:
        return redirect(next_url)

    # Detail-URL bevorzugen (expenses-first), sonst Liste
    for name in ("exp_draft_detail","expenses_draft_detail","expense_draft_detail",
                 "inv_draft_detail","draft_detail"):
        try:
            return redirect(reverse(name, args=[d.pk]))
        except NoReverseMatch:
            continue

    return redirect("/crm/expenses/drafts/")




# --- AI FIX begin (safe append) ---
from django.db.models.fields.files import FileField as _FF

def _first_filefield_name(obj):
    for f in obj._meta.fields:
        if isinstance(f, _FF):
            return f.name
    return None

def _attach_pdf(draft, pdf_bytes: bytes, filename: str='mail.pdf'):
    name = _first_filefield_name(draft) or 'pdf'
    if hasattr(draft, name):
        getattr(draft, name).save(filename, ContentFile(pdf_bytes), save=False)

def _is_decimal_field(f): return isinstance(f, models.DecimalField)
def _is_date_field(f):    return isinstance(f, (models.DateField,))
def _is_char_field(f):    return isinstance(f, (models.CharField, models.TextField))

def _best_field_by_tokens(obj, tokens, type_pred):
    cand = []
    for f in obj._meta.fields:
        if not type_pred(f):
            continue
        name = f.name.lower()
        if any(tok in name for tok in tokens):
            cand.append((name.count("_"), len(name), f))
    if not cand:
        return None
    cand.sort()
    return cand[0][2].name

def _assign_amount(obj, value, aliases, tokens):
    if value is None: return None
    for nm in aliases:
        if hasattr(obj, nm):
            setattr(obj, nm, value); return nm
    f = _best_field_by_tokens(obj, tokens, _is_decimal_field)
    if f and hasattr(obj, f): setattr(obj, f, value); return f
    return None

def _assign_text(obj, value, aliases, tokens):
    if not value: return None
    for nm in aliases:
        if hasattr(obj, nm):
            setattr(obj, nm, value); return nm
    f = _best_field_by_tokens(obj, tokens, _is_char_field)
    if f and hasattr(obj, f): setattr(obj, f, value); return f
    return None

def _assign_date(obj, value, aliases, tokens):
    if not value: return None
    for nm in aliases:
        if hasattr(obj, nm):
            setattr(obj, nm, value); return nm
    f = _best_field_by_tokens(obj, tokens, _is_date_field)
    if f and hasattr(obj, f): setattr(obj, f, value); return f
    return None

def _populate_generic_from_pdf(draft, pdf_bytes: bytes):
    text = extract_text(pdf_bytes)
    net, vat, gross, rate = find_amounts(text)
    try:
        if isinstance(rate, Decimal): rate = rate.quantize(Decimal('1'))
    except Exception:
        pass

    A_GROSS = ['gross_amount','amount_brutto','brutto','total','amount_total','betrag_brutto','gesamt','rechnungsbetrag', 'amount']

    A_NET   = ['net_amount','amount_netto','netto','net','subtotal','zwischensumme', 'amount']

    A_VAT   = ['vat_amount','tax_amount','mwst_betrag','ust_betrag','mwst','ust','umsatzsteuer','steuer_betrag']
    A_RATE  = ['vat_rate','tax_rate','mwst_satz','ust_satz','steuersatz','ust_prozent','mwst_prozent','mwst_pct','ust_pct']
    A_DATE  = ['invoice_date','date','datum','belegdatum','rechnungsdatum','doc_date']
    A_ISS   = ['issuer','vendor','supplier','creditor','payee','unternehmen','company','firma','lieferant']

    T_GROSS = ['gross','brutt','total','gesamt','sum','rechnungsbetrag']
    T_NET   = ['net','nett','subtotal','zwischensumme']
    T_VAT   = ['vat','ust','mwst','steuer','tax']
    T_RATE  = ['rate','satz','percent','proz','pct']
    T_DATE  = ['date','datum']
    T_ISS   = ['issuer','vendor','supplier','creditor','payee','unterneh','firma','lieferant','company']

    if vat is None and (gross is not None and net is not None):
        vat = (gross - net)

    set_fields = {}
    set_fields['gross']  = _assign_amount(draft, gross, A_GROSS, T_GROSS)
    set_fields['net']    = _assign_amount(draft, net,   A_NET,   T_NET)
    set_fields['vat']    = _assign_amount(draft, vat,   A_VAT,   T_VAT)
    set_fields['rate']   = _assign_amount(draft, rate,  A_RATE,  T_RATE)
    set_fields['date']   = _assign_date(  draft, find_invoice_date(text), A_DATE, T_DATE)
    set_fields['issuer'] = _assign_text(  draft, find_issuer(text, getattr(draft,'issuer','') or ''), A_ISS, T_ISS)    # Beschreibung auffüllen, falls leer
    try:
        desc_empty = (not getattr(draft, 'description', ''))
    except Exception:
        desc_empty = False
    if desc_empty and hasattr(draft, 'description'):
        parts = []
        try:
            if issuer: parts.append(str(issuer))
        except Exception: pass
        try:
            if inv_date: parts.append(str(inv_date))
        except Exception: pass
        try:
            if gross is not None: parts.append(f"{gross} EUR")
        except Exception: pass
        draft.description = " – ".join([p for p in parts if p]) or "Rechnung"



    if hasattr(draft, 'raw_text'):
        draft.raw_text = text[:20000]

    try: print("🌱 populate fields ->", set_fields)
    except Exception: pass

def _get_draft_model():
    for app_label, model_name in [('crm_core','ExpenseDraft'),
                                  ('crm_core','InvoiceDraft'),
                                  ('expenses','ExpenseDraft'),
                                  ('invoices','InvoiceDraft')]:
        try:
            m = apps.get_model(app_label, model_name)
            if m: return m
        except Exception:
            pass
    try:
        from .models_invoices import InvoiceDraft
        return InvoiceDraft
    except Exception:
        return None

@login_required
def draft_from_email(request):
    mid = request.GET.get("mid"); aid = request.GET.get("aid")
    download = request.GET.get("download"); next_url = request.GET.get("next")
    pdf_bytes = None; filename = "mail.pdf"

    if download:
        try:
            r = requests.get(download, timeout=30)
            if r.status_code >= 400 or not r.content:
                return HttpResponseBadRequest("Download fehlgeschlagen.")
            pdf_bytes = r.content
            try:
                from urllib.parse import urlparse
                fn = urlparse(download).path.rsplit("/",1)[-1]
                if fn: filename = fn
            except Exception: pass
        except Exception:
            return HttpResponseBadRequest("Download fehlgeschlagen (Netzwerk).")
    elif mid:
        sess = get_ms_session(request)
        if not sess: return HttpResponseBadRequest("Kein MS-Session-Token verfügbar.")
        try:
            atts = list_attachments(sess, mid)
        except Exception:
            return HttpResponseBadRequest("Anhänge konnten nicht geladen werden.")
        if aid:
            pick = next((a for a in atts if a.get("id")==aid), None)
            if not pick: return HttpResponseBadRequest("Attachment nicht gefunden.")
        else:
            pdfs = [a for a in atts if str(a.get("contentType","")).lower().startswith("application/pdf") or str(a.get("name","")).lower().endswith(".pdf")]
            if not pdfs: return HttpResponseBadRequest("Kein PDF-Anhang gefunden.")
            pick = pdfs[0]
        try:
            pdf_bytes = fetch_attachment_bytes(sess, mid, pick["id"])
        except Exception:
            return HttpResponseBadRequest("Attachment-Download fehlgeschlagen.")
        filename = pick.get("name") or filename
    else:
        return HttpResponseBadRequest("Erwarte (?mid[&aid]) oder (?download=URL).")

    DraftModel = _get_draft_model()
    if DraftModel is None: return HttpResponseBadRequest("Draft-Modell nicht gefunden.")

    d = DraftModel()
    if hasattr(d, "status"):
        try: d.status = "draft"
        except Exception: pass
    if hasattr(d, "created_by") and getattr(request, "user", None) and request.user.is_authenticated:
        d.created_by = request.user
    d.save()

    _attach_pdf(d, pdf_bytes, filename=filename or "mail.pdf")
    _populate_generic_from_pdf(d, pdf_bytes)
    d.save()

    messages.success(request, "Rechnung als Entwurf vorgemerkt.")

    if next_url: return redirect(next_url)

    for name in ("exp_draft_detail","expenses_draft_detail","expense_draft_detail",
                 "inv_draft_detail","draft_detail"):
        try: return redirect(reverse(name, args=[d.pk]))
        except NoReverseMatch: continue

    return redirect("/crm/expenses/drafts/")
# --- AI FIX end ---

# --- EXPENSE ENRICH HELPERS begin ---
from .invoice_extract import extract_text, find_amounts, find_invoice_date, find_issuer
def _populate_expense_from_pdf_bytes(exp, pdf_bytes: bytes):
    try:
        text = extract_text(pdf_bytes)
    except Exception:
        text = ""
    net, vat, gross, rate = find_amounts(text)

    # amount = Brutto
    try:
        if hasattr(exp,'amount') and gross is not None:
            exp.amount = gross
    except Exception: pass

    # Supplier
    try:
        issuer = find_issuer(text, getattr(exp,'supplier','') or '')
        if issuer and hasattr(exp,'supplier'):
            exp.supplier = issuer
    except Exception: pass

    # Datum
    try:
        inv_date = find_invoice_date(text)
        if inv_date and hasattr(exp,'date'):
            exp.date = inv_date
    except Exception: pass

    # Beschreibung nur setzen, wenn leer
    try:
        if hasattr(exp,'description') and not getattr(exp,'description',''):
            parts=[]
            try:
                if issuer: parts.append(str(issuer))
            except Exception: pass
            try:
                if inv_date: parts.append(str(inv_date))
            except Exception: pass
            try:
                if gross is not None: parts.append(f"{gross} EUR")
            except Exception: pass
            exp.description = " – ".join([p for p in parts if p]) or "Rechnung"
    except Exception: pass
# --- EXPENSE ENRICH HELPERS end ---

# --- compat wrapper: /invoices/draft/from-email/ ---
def draft_from_email_compat(request):
    """
    Accepts mid/aid and many aliases; auto-picks first PDF if only mid is given.
    Logs for debugging and then forwards to draft_from_email().
    """
    try:
        qs = request.GET.copy()
        def _q(*names):
            for n in names:
                v = (qs.get(n) or request.POST.get(n) or "").strip()
                if v:
                    return v
            return None

        mid = _q("mid","message_id","mail","mail_id","message","email")
        aid = _q("aid","attachment_id","att","anhang","anhang_id")
        download = _q("download","url","href","pick")
        print(f"INV-FROM-EMAIL compat: path={request.path} mid={mid} aid={aid} download_or_pick={'yes' if download else 'no'}")

        if mid and not aid:
            try:
                from .ms_graph_helpers import list_attachments  # type: ignore
                sess = None
                try:
                    if "get_ms_session" in globals():
                        sess = get_ms_session(request)  # type: ignore
                except Exception as _e_sess:
                    print("INV-FROM-EMAIL compat: get_ms_session failed:", _e_sess)
                if list_attachments and sess:
                    atts = list_attachments(sess, mid) or []
                    pick = next((a for a in atts if (str(a.get("contentType","")).lower()=="application/pdf"
                                                     or str(a.get("name","")).lower().endswith(".pdf"))), None)
                    if pick:
                        aid = pick.get("id")
                        print(f"INV-FROM-EMAIL compat: auto-picked attachment id={aid} name={pick.get('name')}")
                        qs["aid"] = aid
            except Exception as e:
                print("INV-FROM-EMAIL compat: auto-pick failed:", e)

        if mid: qs["mid"] = mid
        if aid: qs["aid"] = aid
        if download: qs["download"] = download
        try:
            request.GET = qs
        except Exception as e:
            print("INV-FROM-EMAIL compat: request.GET replace failed:", e)

        if not download and not (mid and aid):
            from django.http import HttpResponse  # type: ignore
            msg = "Bitte den Button neben einem konkreten Anhang benutzen – es fehlen Parameter (mid/aid)."
            print("INV-FROM-EMAIL compat:", msg, "qs_raw=", dict(qs))
            return HttpResponse(msg, status=400)
    except Exception as e:
        print("INV-FROM-EMAIL compat: normalization failed:", e)
    return draft_from_email(request)
