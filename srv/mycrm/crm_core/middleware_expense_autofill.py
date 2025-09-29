
from django.utils.deprecation import MiddlewareMixin
import logging, importlib, os
from pathlib import Path

logger = logging.getLogger(__name__)

AMOUNT_KEYS = {"amount","total","brutto","gross","gross_amount","betrag","summe","total_amount","total_gross"}
VENDOR_KEYS = {"vendor","lieferant","supplier","firma","empfaenger"}
DATE_KEYS   = {"date","invoice_date","rechnungsdatum"}
INVNO_KEYS  = {"invoice_number","rechnungsnummer","belegnummer","belegnr"}
# auch Query-Param Namen, über die wir an eine Attachment- oder Mail-ID kommen könnten:
ATT_KEYS    = ("attachment","attachment_id","att","anhang","anhang_id")
MAIL_KEYS   = ("email","email_id","mail","mail_id","message","message_id")

def _resolve_attachment(pk):
    # Versuche mehrere Modelle, wie bereits in views_ocr.py
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
                for f in ("file","document","attachment","content","blob"):
                    if hasattr(obj, f):
                        filefield = getattr(obj, f)
                        path = getattr(filefield, "path", None) or getattr(filefield, "name", None)
                        ctype = getattr(filefield, "content_type", None) or getattr(obj, "content_type", None)
                        if path:
                            return str(path), ctype
        except Exception as ex:
            logger.debug("Autofill: resolve %s.%s failed: %s", mod, cls, ex)
    return None, None

def _find_attachment_for_mail(mail_pk):
    # Versuche Mail-Modelle zu finden und wähle 'beste' PDF-Rechnung
    candidates = [
        ("crm_mail.models", "Email"),
        ("mail.models", "Email"),
        ("crm_core.models", "Email"),
        ("crm_mail.models", "Message"),
    ]
    for mod, cls in candidates:
        try:
            m = importlib.import_module(mod)
            C = getattr(m, cls, None)
            if C is None: continue
            msg = C.objects.filter(pk=mail_pk).first()
            if not msg: continue
            atts = []
            for relname in ("attachments","attachment_set","files"):
                if hasattr(msg, relname):
                    rel = getattr(msg, relname)
                    try:
                        atts = list(rel.all())
                    except Exception:
                        atts = list(rel)
                    break
            # Scoring: nimm PDF mit Rechnungs-Indizien, sonst erstes PDF
            best = None
            score = -1
            for a in atts:
                path = getattr(getattr(a, "file", a), "path", None) or getattr(getattr(a, "document", a), "path", None)
                name = (getattr(getattr(a, "file", a), "name", None) or getattr(getattr(a, "document", a), "name", "") or "").lower()
                if not (path or name): continue
                if not (name.endswith(".pdf") or str(path).lower().endswith(".pdf")): continue
                s = 0
                for kw in ("rechnung","invoice","deepl","microsoft","selfnet","re","di-"):
                    if kw in name: s += 2
                if name.startswith("re") or "rechnung" in name: s += 3
                if s > score:
                    best, score = (path or name), s
            if best:
                return best, "application/pdf"
        except Exception as ex:
            logger.debug("Autofill: mail lookup %s.%s failed: %s", mod, cls, ex)
    return None, None

def _inject_if_empty(data, keys, value, *, money=False):
    if value in (None, "", 0, 0.0): return
    for k in list(data.keys()) + list(keys):
        kk = k if k in data else k
        if kk in keys:
            cur = str(data.get(kk, "")).strip()
            if (not cur) or cur in ("0","0.0","0,0","0,00","0.00"):
                if money:
                    # HTML number expects dot; text fields oft mit Komma – wir lassen Normalisierung dem DecimalCommaMiddleware
                    data[kk] = str(value)
                else:
                    data[kk] = value

class ExpenseAutofillMiddleware(MiddlewareMixin):
    """
    Füllt POST-Daten für Buchhaltungs-/Vormerk-Aktionen aus Anhang/Mail per OCR,
    wenn Betrag/Datum/Rechnungsnr./Lieferant fehlen oder 0 sind.
    """
    def process_request(self, request):
        if request.method != "POST":
            return None

        # Greife so breit wie nötig – viele Projekte haben eigene Endpunkte:
        # typische Pfade für Ausgaben und Mailaktionen
        path = request.path.lower()
        if not any(p in path for p in ("/crm/expense", "/crm/expenses", "/crm/buchhaltung", "/crm/mail", "/mail/")):
            return None

        # Attachment-ID?
        att_id = None
        for k in ATT_KEYS:
            att_id = att_id or request.POST.get(k) or request.GET.get(k)
        # Mail-ID als Fallback?
        mail_id = None
        for k in MAIL_KEYS:
            mail_id = mail_id or request.POST.get(k) or request.GET.get(k)

        # Wenn weder noch – nichts tun
        if not att_id and not mail_id:
            return None

        path_ct = None
        if att_id:
            try:
                path_ct = _resolve_attachment(int(att_id))
            except Exception:
                path_ct = _resolve_attachment(att_id)
        elif mail_id:
            try:
                path_ct = _find_attachment_for_mail(int(mail_id))
            except Exception:
                path_ct = _find_attachment_for_mail(mail_id)

        if not path_ct or not path_ct[0]:
            logger.warning("Autofill: kein Anhang gefunden (att=%s mail=%s)", att_id, mail_id)
            return None

        file_path, ctype = path_ct
        try:
            # Lazy import, um Zyklen zu vermeiden
            from crm_core.ocr_invoice import extract_text, parse_invoice_text
            txt = extract_text(file_path, ctype)
            data = parse_invoice_text(txt, source_path=file_path) if "source_path" in parse_invoice_text.__code__.co_varnames else parse_invoice_text(txt)
        except Exception as ex:
            logger.exception("Autofill: OCR/Parse-Fehler für %s: %s", file_path, ex)
            return None

        if not data:
            return None

        # POST kopieren & befüllen
        try:
            post = request.POST.copy()
            # Betrag
            amt = data.get("total")
            _inject_if_empty(post, AMOUNT_KEYS, amt, money=True)
            # Lieferant
            vend = data.get("vendor") or data.get("vendor_guess")
            _inject_if_empty(post, VENDOR_KEYS, vend)
            # Datum
            _inject_if_empty(post, DATE_KEYS, data.get("date"))
            # Rechnungsnummer
            _inject_if_empty(post, INVNO_KEYS, data.get("invoice_number"))

            request.POST = post
            logger.warning("Autofill: Betrag=%s, Vendor=%s, Date=%s, Inv=%s aus %s",
                           data.get("total"), vend, data.get("date"), data.get("invoice_number"),
                           os.path.basename(str(file_path)))
        except Exception as ex:
            logger.debug("Autofill: konnte POST nicht setzen: %s", ex)

        return None
