# -*- coding: utf-8 -*-
import re
from datetime import datetime, date

_NUM = r"(?:\d{1,3}(?:[.\s]\d{3})*(?:[.,]\d{2})|\d+[.,]\d{2})"

def _to_float(num_str: str) -> float | None:
    if not num_str:
        return None
    s = num_str.strip()
    # 1.234,56 -> 1234.56 ; 1,234.56 -> 1234.56 ; 1234 -> 1234.00 (falls ohne Dezimal)
    if "," in s and "." in s:
        # Heuristik: letzter Trenner ist Dezimal
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        # 12,34 -> 12.34 | 1,234 -> 1234 (wenn nach Komma mehr als 2 Ziffern -> tausennder raus)
        parts = s.split(",")
        if len(parts[-1]) <= 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")
    else:
        # nur Punkte -> wenn Dezimal-Länge <=2, sonst Tausender raus
        parts = s.split(".")
        if len(parts) > 1 and len(parts[-1]) <= 2:
            pass
        else:
            s = s.replace(".", "")
    try:
        return float(s)
    except Exception:
        return None

_DATE_RX = re.compile(
    r"\b(?:(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})|(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2}))\b"
)

_VAT_HINT = re.compile(r"\b(ust|mwst|umsatzsteuer|vat)\b", re.I)
_VAT_RATE = re.compile(r"(\d{1,2}(?:[.,]\d)?)\s*%", re.I)

_AMOUNT_HINT = re.compile(
    r"(brutto|gesamt(?:summe)?|summe|total|amount|zu\s*zahlen|payable|invoice\s*total)",
    re.I
)

def _pick_best_date(text: str) -> str:
    best = None
    for m in _DATE_RX.finditer(text or ""):
        if m.group(1):
            d, mth, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        else:
            y, mth, d = int(m.group(4)), int(m.group(5)), int(m.group(6))
        try:
            dt = date(y, mth, d)
        except ValueError:
            continue
        # Plausibilität: 2010..heute+1
        if date(2010,1,1) <= dt <= date.today().replace(year=date.today().year+1):
            best = dt
            break
    return best.isoformat() if best else ""

def _candidates_amounts(text: str) -> list[tuple[float, int]]:
    out = []
    for m in re.finditer(_NUM, text or ""):
        val = _to_float(m.group(0))
        if val is None:
            continue
        # IBANs & große Zahlen filtern: typisch 0<val<1e7
        if 0 < val < 10_000_000:
            out.append((val, m.start()))
    return out

def _hinted_amount(text: str) -> float | None:
    # Nimmt die Zahl, die am nächsten an einem "Summe/Brutto/Total"-Hint steht
    best = None
    for line in (text or "").splitlines():
        if _AMOUNT_HINT.search(line):
            # suche Zahl in derselben Zeile, nimm die größte
            nums = [( _to_float(m.group(0)) or 0.0 ) for m in re.finditer(_NUM, line)]
            nums = [n for n in nums if n > 0]
            if nums:
                cand = max(nums)
                if (best or 0) < cand:
                    best = cand
    return best

def _vat_rate(text: str) -> float | None:
    # Suche Zeilen mit VAT-Hint, dann Prozent darin
    rate = None
    for line in (text or "").splitlines():
        if _VAT_HINT.search(line):
            ms = _VAT_RATE.findall(line)
            for r in ms:
                v = _to_float(r)
                if v is not None and 0 < v <= 30:
                    rate = v if (rate is None or v > rate) else rate
    return rate

def extract_invoice_numbers(text: str) -> dict:
    """
    Liefert Dict: {"brutto": float|None, "datum": "YYYY-MM-DD"|"" , "ust_satz": float|None}
    """
    res = {"brutto": None, "datum": "", "ust_satz": None}

    # Datum
    res["datum"] = _pick_best_date(text or "")

    # USt-Satz
    rate = _vat_rate(text or "")
    if rate is not None:
        res["ust_satz"] = rate

    # Betrag – erst mit Hints (Summe/Brutto/Total), sonst global größter plausibler Betrag
    b = _hinted_amount(text or "")
    if b is None:
        cands = _candidates_amounts(text or "")
        if cands:
            cands.sort(key=lambda t: t[0], reverse=True)
            b = cands[0][0]
    res["brutto"] = b
    return res
