# /srv/mycrm/crm_core/ocr_invoices.py
from pathlib import Path
import re, subprocess, tempfile
from decimal import Decimal, InvalidOperation
from datetime import datetime
import pytesseract
from PIL import Image

# ---- Hilfen ---------------------------------------------------
_AMOUNT = re.compile(r"""
 (?:
   Gesamtbetrag|Gesamt|Summe|Total|Betrag|Amount
 )\D{0,15}
 ([0-9]{1,3}(?:[.\s][0-9]{3})*(?:,[0-9]{2})|[0-9]+,[0-9]{2})
""", re.I | re.X)

_INVOICE = re.compile(r"""
 (?:
   Rechnungs(?:nr\.?|nummer)|Re-Nr\.?|Invoice(?:\s*No\.?)?
 )\D{0,10}([A-Z0-9\-/.]{3,})
""", re.I | re.X)

_DATE = re.compile(r"""
 (?:
   Rechnungsdatum|Datum|Date|Issue(?:d)?\s*on
 )\D{0,10}
 (\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4})
""", re.I | re.X)

def _norm_decimal(s: str) -> Decimal | None:
    s = s.strip().replace(" ", "").replace(".", "").replace("€","").replace("EUR","")
    s = s.replace(",", ".")
    try:
        return Decimal(s)
    except (InvalidOperation, ValueError):
        return None

def _norm_date(s: str) -> datetime | None:
    s = s.strip().replace(" ", "")
    for fmt in ("%d.%m.%Y", "%d.%m.%y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    # dd/mm/yyyy
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        d,mn,y = map(int, m.groups())
        try: return datetime(y, mn, d)
        except ValueError: pass
    return None

def _pdf_to_text_ocr(pdf_path: Path) -> str:
    # Schnell & robust: pdftoppm -> PNG -> Tesseract
    text_parts = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td) / "page"
        # 200 DPI reicht idR, 300 für knifflige Scans
        subprocess.run(["pdftoppm", "-r", "200", "-png", str(pdf_path), str(base)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for img in sorted(Path(td).glob("page-*.png")):
            im = Image.open(img)
            # deutsch + englisch hilft bei gemischten Belegen
            text_parts.append(pytesseract.image_to_string(im, lang="deu+eng"))
    return "\n".join(text_parts)

def extract_invoice_data(pdf_path: str) -> dict:
    p = Path(pdf_path)
    text = ""
    try:
        text = _pdf_to_text_ocr(p)
    except Exception as e:
        text = ""

    t = (text or "").replace("\xa0", " ")

    amt = None; inv = None; dt = None; vendor = None

    m = _AMOUNT.search(t)
    if m:
        amt = _norm_decimal(m.group(1))

    m = _INVOICE.search(t)
    if m:
        inv = m.group(1).strip().strip(" .,:;")

    m = _DATE.search(t)
    if m:
        dt = _norm_date(m.group(1))

    # Vendor-Heuristik (einfach, funktioniert bei Microsoft/DeepL/Selfnet gut)
    if re.search(r"\bDeepL\b", t, re.I): vendor = "DeepL"
    elif re.search(r"\bMicrosoft\b", t, re.I): vendor = "Microsoft"
    elif re.search(r"\bSelfnet\b", t, re.I): vendor = "Selfnet"

    return {
        "amount": amt,             # Decimal|None
        "invoice_no": inv,         # str|None
        "invoice_date": dt.date().isoformat() if dt else None,
        "vendor": vendor,
        "raw_excerpt": t[:500],    # fürs Debugging im Log
    }
