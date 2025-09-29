
import re, subprocess, shlex, os, tempfile, glob
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

# -------- helpers --------
def _run(cmd: str, input=None, timeout=45) -> Tuple[int, str, str]:
    p = subprocess.Popen(shlex.split(cmd), stdin=subprocess.PIPE if input else None,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(input=input, timeout=timeout)
    return p.returncode, out or "", err or ""

def _clean(s: str) -> str:
    s = s.replace("\r\n","\n").replace("\r","\n")
    return re.sub(r"[ \t]+"," ", s)

def _to_float_de(x: str) -> Optional[float]:
    if not x: return None
    x = re.sub(r"[.\s]", "", x.strip())   # tausender
    x = x.replace(",", ".")
    try: return float(x)
    except: return None

# -------- text extraction --------
def _extract_text_pdf(path: str) -> str:
    # 1) pdftotext
    rc, out, err = _run(f"pdftotext -layout -nopgbrk {shlex.quote(path)} -")
    if rc == 0 and out.strip():
        return _clean(out)
    # 2) pdfminer (falls installiert)
    try:
        from pdfminer.high_level import extract_text
        t = extract_text(path) or ""
        if t.strip(): return _clean(t)
    except Exception:
        pass
    # 3) OCR über pdftoppm + tesseract
    txt_chunks = []
    with tempfile.TemporaryDirectory() as td:
        base = os.path.join(td, "p")
        rc, _, _ = _run(f"pdftoppm -png -r 300 {shlex.quote(path)} {shlex.quote(base)}")
        for img in sorted(glob.glob(base+"-*.png")):
            rc, out, err = _run(f"tesseract {shlex.quote(img)} stdout --psm 6 -l deu+eng")
            if out.strip():
                txt_chunks.append(out)
    return _clean("\n".join(txt_chunks))

def _extract_text_image(path: str) -> str:
    # 1) tesseract
    rc, out, err = _run(f"tesseract {shlex.quote(path)} stdout --psm 6 -l deu+eng")
    if rc == 0 and out.strip():
        return _clean(out)
    # 2) pytesseract (falls vorhanden)
    try:
        import pytesseract
        from PIL import Image
        t = pytesseract.image_to_string(Image.open(path), lang="deu+eng") or ""
        if t.strip(): return _clean(t)
    except Exception:
        pass
    return ""

def extract_text(path: str, content_type: Optional[str]=None) -> str:
    lower = (path or "").lower()
    if (content_type and "pdf" in content_type.lower()) or lower.endswith(".pdf"):
        return _extract_text_pdf(path)
    if lower.endswith((".png",".jpg",".jpeg",".tif",".tiff",".bmp",".webp")):
        return _extract_text_image(path)
    # fallback
    t = _extract_text_pdf(path)
    return t or _extract_text_image(path)

# -------- parsing --------
_NUM = r"(?:\\d{1,3}(?:[.\\s]\\d{3})*(?:[.,]\\d{2})|\\d+(?:[.,]\\d{2})?)"
_CUR = r"(?:EUR|€)"
_DATE = r"(?:\\d{2}\\.\\d{2}\\.\\d{4}|\\d{4}-\\d{2}-\\d{2})"
_IBAN = r"\\b[A-Z]{2}\\d{2}[A-Z0-9]{11,30}\\b"

def _parse_from_filename(path: str) -> Dict[str, Any]:
    name = os.path.basename(path or "").lower()
    out: Dict[str, Any] = {}
    # DeepL: invoice_DI-20250911-886.pdf
    m = re.search(r"\\bdi-(\\d{8})-(\\d+)\\b", name, re.I)
    if m:
        out["invoice_number"] = f"DI-{m.group(1)}-{m.group(2)}"
        y,mn,d = m.group(1)[:4], m.group(1)[4:6], m.group(1)[6:8]
        out["date"] = f"{y}-{mn}-{d}"
        out["vendor"] = out.get("vendor") or "DeepL"
    # Selfnet: RE250900095
    m = re.search(r"\\bre\\d{9,}\\b", name, re.I)
    if m:
        out["invoice_number"] = m.group(0).upper()
        out["vendor"] = out.get("vendor") or "Selfnet"
    # Microsoft: rein numerische lange Nummer
    m = re.search(r"\\b(\\d{10,})\\b", name)
    if m:
        out.setdefault("invoice_number", m.group(1))
        out["vendor"] = out.get("vendor") or "Microsoft"
    # Vendor hint aus Name
    for v, tag in (("Microsoft","microsoft"),("Selfnet","selfnet"),("DeepL","deepl")):
        if tag in name: out["vendor"] = out.get("vendor") or v
    return out

def parse_invoice_text(text: str, *, source_path: Optional[str]=None) -> Dict[str, Any]:
    t = _clean(text or "")
    out: Dict[str, Any] = {"raw": t}

    # --- Dateiname-Fallback zuerst mergen ---
    if source_path:
        out.update({k:v for k,v in _parse_from_filename(source_path).items() if v})

    # IBAN
    iban = re.search(_IBAN, t.replace(" ", ""))
    if not iban:
        iban = re.search(_IBAN, t)
    if iban:
        out["iban"] = iban.group(0)

    # Rechnungsnummer
    m = re.search(r"(Rechnungs?(?:nummer|nr\\.?)[^\\S\\n]*[:\\-]?[\\s]*([A-Z0-9\\-\\/\\.]+))", t, re.I)
    if not m and "invoice_number" not in out:
        # weitere Heuristik: "Invoice number"
        m = re.search(r"(Invoice\\s+Number|Invoice No\\.?)[^\\S\\n]*[:\\-]?[\\s]*([A-Z0-9\\-\\/\\.]+)", t, re.I)
    if m and not out.get("invoice_number"):
        out["invoice_number"] = m.group(2)

    # Datum
    m = re.search(r"(Rechnungsdatum|Datum|Invoice\\s+Date)[^\\S\\n]*[:\\-]?[\\s]*("+_DATE+")", t, re.I)
    if not m:
        m = re.search(_DATE, t)
    if m and not out.get("date"):
        out["date"] = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(0)

    # Betrag (Total/Brutto)
    m = re.search(r"(Gesamt(?:betrag)?|Brutto|Rechnungsbetrag|Summe|Total|Amount)[^\\S\\n]*[:\\-]?[\\s]*("+_NUM+")\\s*("+_CUR+")?", t, re.I)
    if not m:
        m = re.search(r"("+_NUM+")\\s*("+_CUR+")", t, re.I)
    if m and not out.get("total"):
        val = m.group(2) if m.lastindex and m.lastindex >= 2 else m.group(1)
        out["total"] = _to_float_de(val)
        out["currency"] = out.get("currency") or "EUR"

    # USt/MwSt
    m = re.search(r"(USt|MwSt|VAT)[^\\S\\n]*[:\\-]?[\\s]*(\\d{1,2}(?:[.,]\\d{1,2})?)\\s*%", t, re.I)
    if m:
        try: out["vat_rate"] = float(m.group(2).replace(",", "."))
        except: pass

    # Vendor aus Kopfzeilen/Impressum
    head = "\\n".join(t.split("\\n")[:15])
    cand = []
    for line in head.split("\\n"):
        L = line.strip()
        if len(L) < 2: continue
        if re.search(r"(rechnung|kundennr|iban|betrag|summe|ust|mwst|invoice|tax|vat)", L, re.I):
            continue
        cand.append(L)
    if cand and not out.get("vendor"):
        out["vendor"] = cand[0][:120]

    # Vendor Overrides per Text
    low = t.lower()
    if "microsoft" in low: out["vendor"] = "Microsoft"
    if "selfnet"  in low: out["vendor"] = "Selfnet"
    if "deepl"    in low: out["vendor"] = "DeepL"

    return out
