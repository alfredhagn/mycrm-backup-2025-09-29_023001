from __future__ import annotations
import hashlib
import re
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Optional, Tuple

# --- Text-Extraktion (pypdf -> pdfminer -> OCR) --------------------------------

def extract_text(pdf_bytes: bytes) -> str:
    # 1) pypdf
    try:
        from pypdf import PdfReader
        r = PdfReader(BytesIO(pdf_bytes))
        parts = []
        for p in r.pages:
            try:
                parts.append(p.extract_text() or "")
            except Exception:
                pass
        txt = "\n".join(parts).strip()
        if txt:
            return txt
    except Exception:
        pass

    # 2) pdfminer.six
    try:
        from pdfminer.high_level import extract_text as pm_extract_text
        txt = pm_extract_text(BytesIO(pdf_bytes)) or ""
        if txt.strip():
            return txt
    except Exception:
        pass

    # 3) OCR-Fallback
    try:
        return ocr_extract_text(pdf_bytes)
    except Exception:
        return ""

def ocr_extract_text(pdf_bytes: bytes) -> str:
    from pdf2image import convert_from_bytes
    import pytesseract
    images = convert_from_bytes(pdf_bytes, dpi=300)
    out = []
    for img in images:
        out.append(pytesseract.image_to_string(img, lang="deu+eng"))
    return "\n".join(out)

# --- Heuristiken für Beträge / Datum / Aussteller ------------------------------

EU_AMOUNT = re.compile(r'(?<!\d)(\d{1,3}(?:[.\s]\d{3})*|\d+)(?:,(\d{2}))?(?!\d)')
PCT = re.compile(r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%')

def _to_decimal(s: str) -> Optional[Decimal]:
    try:
        s = s.replace(" ", "").replace(".", "").replace(",", ".")
        return Decimal(s)
    except Exception:
        return None


def find_amounts(text: str) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal], Optional[Decimal]]:
    """
    Rückgabe: (netto, mwst_betrag, brutto, mwst_satz_prozent)
    Robuster gegen OCR-Fehler, IDs, Telefonnummern usw.
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    n = len(lines)
    lower_idx = max(0, int(n * 0.6))  # unterer Teil wird stärker gewichtet

    KEY_GROSS = ("brutto","gesamt","gesamtbetrag","summe","total","amount due","fällig","payable")
    KEY_NET   = ("netto","zwischensumme","subtotal","net amount")
    KEY_VAT   = ("mwst","m.w.st","ust","u.st","vat","tax")
    IGNORE    = ("iban","bic","steuernummer","ust-id","ustid","kundennummer","bestellnummer","telefon","tel.","fax","hrb","swift","konto","blz")

    AMOUNT_RE = re.compile(r'(?<!\d)(-?\d{1,3}(?:[.\s\'’]\d{3})*|-?\d+)(?:,(\d{2}))?(?!\d)')

    def parse_amounts(line: str):
        """liefert (Decimal, integer_digits, raw) für jeden Treffer in der Zeile"""
        out = []
        for m in AMOUNT_RE.finditer(line):
            whole, cents = m.group(1), m.group(2)
            raw = whole + ("," + cents if cents else "")
            cleaned = whole.replace(" ", "").replace(".", "").replace("'", "").replace("’", "")
            if not cleaned or cleaned in ("-",):
                continue
            # zu lange Integerteile wegfiltern (IDs)
            neg = cleaned.startswith("-")
            if neg:
                cleaned_i = cleaned[1:]
            else:
                cleaned_i = cleaned
            integer_part = cleaned_i.split(",")[0]
            if len(integer_part) > 7:  # > 9,999,999: sehr unwahrscheinlich als Rechnungsbetrag
                continue
            try:
                val = Decimal(( "-" if neg else "" ) + cleaned_i.replace(",", "."))
            except Exception:
                continue
            out.append((val, len(integer_part), raw))
        return out

    def has_kw(line: str, kws):
        L = line.lower()
        return any(k in L for k in kws)

    def has_currency(line: str):
        L = line.lower()
        return ("€" in L) or (" eur" in L) or ("eur " in L) or (" chf" in L) or (" usd" in L) or ("$" in L)

    # Kandidaten sammeln
    cand_net, cand_vat, cand_gross = [], [], []
    vat_rate = None

    PCT = re.compile(r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%')
    for idx, line in enumerate(lines):
        low = line.lower()

        # ignorierbare Zeilen
        if any(k in low for k in IGNORE):
            continue

        # MwSt-Satz extrahieren
        if vat_rate is None:
            mrate = PCT.search(low)
            if mrate:
                try:
                    vat_rate = Decimal(mrate.group(1).replace(",", "."))
                except Exception:
                    pass

        amts = parse_amounts(line)
        if not amts:
            continue

        # Score-Grundlage
        weight = 2 if idx >= lower_idx else 1
        cur = 1 if has_currency(line) else 0

        if has_kw(low, KEY_GROSS):
            for v, _, raw in amts:
                if v is None or v <= 0 or v >= Decimal("1000000"):
                    continue
                cand_gross.append((v, 100*weight + 10*cur, idx, line))
        if has_kw(low, KEY_NET):
            for v, _, raw in amts:
                if v is None or v <= 0 or v >= Decimal("1000000"):
                    continue
                cand_net.append((v, 80*weight + 10*cur, idx, line))
        if has_kw(low, KEY_VAT):
            for v, _, raw in amts:
                if v is None or v <= 0 or v >= Decimal("1000000"):
                    continue
                cand_vat.append((v, 70*weight + 10*cur, idx, line))

        # Falls keine Keywords: letzte Beträge im unteren Drittel als schwache Kandidaten
        if not (has_kw(low, KEY_NET) or has_kw(low, KEY_VAT) or has_kw(low, KEY_GROSS)):
            for v, _, raw in amts:
                if v is None or v <= 0 or v >= Decimal("1000000"):
                    continue
                if idx >= lower_idx:
                    cand_gross.append((v, 5*weight + cur, idx, line))  # sehr schwach

    # Wenn gar nichts gefunden wurde, None zurück
    if not (cand_net or cand_vat or cand_gross):
        return None, None, None, vat_rate

    # Beste Kandidaten nach Score
    cand_net.sort(key=lambda x: (-x[1], x[2]))
    cand_vat.sort(key=lambda x: (-x[1], x[2]))
    cand_gross.sort(key=lambda x: (-x[1], x[2]))

    # Hilfsfunktion: kombiniere zu konsistenter Summe
    def best_combo():
        best = (None, None, None, Decimal("1e9"))
        # 1) bevorzuge Kombination mit klar markiertem Brutto
        bases = cand_gross[:10] or cand_net[:10]
        for g, sg, ig, lg in bases:
            nets = cand_net[:10] or [(None,0,0,"")]
            vats = cand_vat[:10] or [(None,0,0,"")]
            for n, sn, in_, ln in nets:
                for t, st, it, lt in vats:
                    # fehlende Größe ableiten
                    gg = g
                    nn = n
                    tt = t
                    if gg is None and (nn is not None and tt is not None):
                        gg = nn + tt
                    if nn is None and (gg is not None and tt is not None):
                        nn = gg - tt
                    if tt is None and (gg is not None and nn is not None):
                        tt = gg - nn
                    # Plausibilität
                    if any(x is None for x in (gg, nn, tt)):
                        continue
                    if gg <= 0 or nn <= 0 or tt < 0:
                        continue
                    if gg >= Decimal("1000000") or nn >= Decimal("1000000") or tt >= Decimal("1000000"):
                        continue
                    # Konsistenzfehler
                    err = abs(gg - (nn + tt))
                    # VAT-Rate prüfen, wenn vorhanden
                    if nn > 0 and tt >= 0 and vat_rate is not None:
                        rate_err = abs((tt / nn * 100) - vat_rate)
                    else:
                        rate_err = Decimal("0")
                    score = err * Decimal("1000") + rate_err  # Konsistenz hat viel Gewicht
                    if score < best[3]:
                        best = (nn, tt, gg, score)
        return best[:3]

    net, vat, gross = best_combo()

    # Fallbacks, falls immer noch leer:
    if gross is None and cand_gross:
        gross = cand_gross[0][0]
    if net is None and cand_net and gross is not None:
        # wähle Netto, das zu Brutto passt
        best = None
        best_err = Decimal("1e9")
        for n, _, _, _ in cand_net[:10]:
            t = gross - n
            if t < 0: 
                continue
            err = abs(gross - (n + t))
            if err < best_err:
                best = (n, t)
                best_err = err
        if best:
            net, vat = best[0], best[1]

    # MwSt-Satz ableiten, falls möglich
    rate = None
    if net and vat and net > 0:
        try:
            rate = (vat / net) * 100
            # unrealistische Sätze ausblenden
            if rate < 3 or rate > 25:
                rate = vat_rate
        except Exception:
            rate = vat_rate
    else:
        rate = vat_rate

    return net, vat, gross, (rate.quantize(Decimal('0.01')) if isinstance(rate, Decimal) else rate)


def find_invoice_number(text: str) -> Optional[str]:
    for line in text.splitlines():
        l = line.lower()
        if any(k in l for k in ("rechnungsnr", "rechnungs-nr", "rechnung nr", "rechnungsnummer", "invoice no", "invoice number")):
            m = re.search(r'([A-Z0-9][A-Z0-9\-\/]{3,})', line, re.I)
            if m:
                return m.group(1)
    return None

def find_invoice_date(text: str) -> Optional[str]:
    # 1) bevorzugt in Zeilen mit Datum-Keywords
    date_pats = [
        re.compile(r'(\d{2}\.\d{2}\.\d{4})'),    # 31.12.2025
        re.compile(r'(\d{4}-\d{2}-\d{2})'),      # 2025-12-31
        re.compile(r'(\d{1,2}\.\d{1,2}\.\d{2,4})'),
    ]
    pref = ("rechnungsdatum", "rechnung vom", "invoice date", "datum", "date:")
    for line in text.splitlines():
        l = line.lower()
        if any(k in l for k in pref):
            for pat in date_pats:
                m = pat.search(line)
                if m:
                    return _normalize_date(m.group(1))
    # 2) erster Treffer irgendwo
    for pat in date_pats:
        m = pat.search(text)
        if m:
            return _normalize_date(m.group(1))
    # 3) optional: dateparser
    try:
        import dateparser  # type: ignore
        dt = dateparser.parse(text, languages=['de','en'], settings={"DATE_ORDER":"DMY"})
        if dt:
            return dt.date().isoformat()
    except Exception:
        pass
    return None

def _normalize_date(s: str) -> str:
    # versucht DD.MM.YYYY / D.M.YYYY / YYYY-MM-DD in ISO zu wandeln
    s = s.strip()
    if "-" in s and len(s) >= 10:
        return s[:10]
    if "." in s:
        parts = s.split(".")
        try:
            d = int(parts[0]); m = int(parts[1]); y = int(parts[2])
            if y < 100:  # 25 -> 2025 (naiv)
                y += 2000
            return f"{y:04d}-{m:02d}-{d:02d}"
        except Exception:
            return s
    return s

def find_issuer(text: str, fallback_from_name: Optional[str]=None) -> Optional[str]:
    head = [l.strip() for l in text.splitlines()[:50] if l.strip()]
    tokens = ("GmbH","SE","Limited","Ltd","Inc.","AG","Microsoft","DeepL","Selfnet","Operations")
    for l in head:
        if any(t in l for t in tokens):
            return l[:255]
    return (head[0][:255] if head else fallback_from_name)

def guess_currency(text: str) -> str:
    if " CHF" in text or "CHF" in text: return "CHF"
    if "$" in text or " USD" in text:  return "USD"
    if "EUR" in text or "€" in text:   return "EUR"
    return "EUR"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

# --- begin label-first amounts extractor ---
def find_amounts_label_first(text: str) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal], Optional[Decimal]]:
    # Rückgabe: (netto, mwst_betrag, brutto, mwst_satz_prozent)
    T = text.replace("\u00a0"," ")
    lines = [ln.strip() for ln in T.splitlines() if ln.strip()]
    KEY_GROSS = ("brutto","gesamt","rechnungsbetrag","gesamtbetrag","total","amount due","payable","summe")
    KEY_NET   = ("netto","zwischensumme","subtotal","net amount")
    KEY_VAT   = ("mwst","m.w.st","ust","u.st","vat","tax","steuer")
    AMT = re.compile(r'(?<!\d)(-?\d{1,3}(?:[.\s\'’]\d{3})*|-?\d+)(?:[.,](\d{2}))?(?!\d)')
    PCT = re.compile(r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%')
    TYPICAL_RATES = (Decimal("20"), Decimal("19"), Decimal("7"), Decimal("10"))

    def parse_amount_pair(pair):
        whole, cents = pair
        s = whole.replace(" ", "").replace(".", "").replace("'", "").replace("’","")
        if cents: s = s + "." + cents
        try:
            v = Decimal(s)
        except Exception:
            return None
        if v <= 0 or v >= Decimal("1000000"):
            return None
        return v

    cand_net, cand_vat, cand_gross = [], [], []
    vat_rate_inline = None

    for idx, ln in enumerate(lines):
        low = ln.lower()
        if vat_rate_inline is None:
            mrate = PCT.search(low)
            if mrate:
                try:
                    vat_rate_inline = Decimal(mrate.group(1).replace(",", "."))
                except Exception:
                    pass
        vals = [parse_amount_pair(m.groups()) for m in AMT.finditer(ln)]
        vals = [v for v in vals if v is not None]
        if any(k in low for k in KEY_GROSS):
            for v in vals: cand_gross.append((idx, v))
        if any(k in low for k in KEY_NET):
            for v in vals: cand_net.append((idx, v))
        if any(k in low for k in KEY_VAT):
            for v in vals: cand_vat.append((idx, v))

    net = cand_net[-1][1] if cand_net else None
    vat = cand_vat[-1][1] if cand_vat else None
    gross = cand_gross[-1][1] if cand_gross else None

    def consistent_triplet(n,t,g):
        if n is not None and t is not None and g is None: g = n + t
        if g is not None and t is not None and n is None: n = g - t
        if g is not None and n is not None and t is None: t = g - n
        return n,t,g

    def combi_error(n,t,g):
        if None in (n,t,g): return Decimal("1e9")
        return abs(g - (n + t))

    net, vat, gross = consistent_triplet(net, vat, gross)

    if combi_error(net, vat, gross) > Decimal("0.05"):
        N = len(lines)
        best = (None,None,None, Decimal("1e9"))
        window = range(max(0, N-30), N)
        for i in window:
            low = lines[i].lower()
            vals_i = [parse_amount_pair(m.groups()) for m in AMT.finditer(lines[i])]
            vals_i = [v for v in vals_i if v is not None]
            if not vals_i: continue
            if any(k in low for k in KEY_GROSS):
                for g in vals_i:
                    around = [j for j in range(max(0,i-6), min(N,i+7))]
                    nets=[]; vats=[]
                    for j in around:
                        l2 = lines[j].lower()
                        vals_j = [parse_amount_pair(m.groups()) for m in AMT.finditer(lines[j])]
                        vals_j = [v for v in vals_j if v is not None]
                        if any(k in l2 for k in KEY_NET): nets += vals_j
                        if any(k in l2 for k in KEY_VAT): vats += vals_j
                    for n in nets or [None]:
                        for t in vats or [None]:
                            nn,tt,gg = consistent_triplet(n,t,g)
                            if None in (nn,tt,gg): continue
                            if nn <= 0 or gg <= 0 or tt < 0: continue
                            e = combi_error(nn,tt,gg)
                            rate_pen = Decimal("0")
                            if nn > 0:
                                try:
                                    r = (tt/nn)*100
                                    rate_pen = min(abs(r-tr) for tr in TYPICAL_RATES)
                                except Exception:
                                    pass
                            score = e*Decimal("1000") + rate_pen
                            if score < best[3]:
                                best = (nn,tt,gg,score)
        n2,t2,g2,_ = best
        if n2 and t2 and g2:
            net, vat, gross = n2,t2,g2

    rate = None
    if net and vat and net > 0:
        try:
            rate = (vat/net)*100
            rate = rate.quantize(Decimal("0.01"))
            if vat_rate_inline is not None and abs(rate - vat_rate_inline) > Decimal("1.0"):
                rate = vat_rate_inline
        except Exception:
            rate = vat_rate_inline
    else:
        rate = vat_rate_inline

    return net, vat, gross, rate

# override
find_amounts = find_amounts_label_first
# --- end label-first amounts extractor ---

# --- begin stricter amounts extractor v3 ---
def find_amounts_v3(text: str) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[Decimal], Optional[Decimal]]:
    T = text.replace("\u00a0"," ")
    lines = [ln.strip() for ln in T.splitlines() if ln.strip()]
    N = len(lines)
    win = lines[max(0, N-60):]  # untere 60 Zeilen

    KEY_GROSS = ("brutto","gesamt","rechnungsbetrag","gesamtbetrag","total","amount due","payable","summe")
    KEY_NET   = ("netto","zwischensumme","subtotal","net amount")
    KEY_VAT   = ("mwst","m.w.st","ust","u.st","vat","tax","steuer")

    AMT = re.compile(r'(?<!\d)(-?\d{1,3}(?:[.\s\'’]\d{3})*|-?\d+)(?:[.,](\d{2}))?(?!\d)')
    PCT = re.compile(r'(\d{1,2}(?:[.,]\d{1,2})?)\s*%')
    TYPICAL = (Decimal("20"), Decimal("19"), Decimal("7"), Decimal("10"))

    def parse_amount_pair(pair):
        whole, cents = pair
        s = whole.replace(" ", "").replace(".", "").replace("'", "").replace("’","")
        if cents: s = s + "." + cents
        try:
            v = Decimal(s)
        except Exception:
            return None
        if v <= 0 or v >= Decimal("1000000"):
            return None
        return v.quantize(Decimal("0.01"))

    vat_rate_inline = None
    cand_g, cand_n, cand_t = [], [], []   # (score, idx, value)

    for i, ln in enumerate(win):
        idx = (N - len(win)) + i
        low = ln.lower()

        if vat_rate_inline is None:
            mr = PCT.search(low)
            if mr:
                try:
                    vat_rate_inline = Decimal(mr.group(1).replace(",", "."))
                except Exception:
                    pass

        vals = [parse_amount_pair(m.groups()) for m in AMT.finditer(ln)]
        vals = [v for v in vals if v is not None]
        if not vals:
            continue

        base = 1 + (i/len(win))  # unten mehr Gewicht
        if any(k in low for k in KEY_GROSS):
            for v in vals: cand_g.append( (100*base, idx, v, ln) )
        if any(k in low for k in KEY_NET):
            for v in vals: cand_n.append( (80*base, idx, v, ln) )
        if any(k in low for k in KEY_VAT):
            for v in vals: cand_t.append( (70*base, idx, v, ln) )

        # schwache Kandidaten im unteren Drittel als Brutto zulassen
        if i > (2*len(win))//3 and not (any(k in low for k in KEY_GROSS+KEY_NET+KEY_VAT)):
            for v in vals: cand_g.append( (5*base, idx, v, ln) )

    # sortieren & Top-Kandidaten beschränken
    cand_g.sort(key=lambda x: (-x[0], x[1])); cand_g = cand_g[:15]
    cand_n.sort(key=lambda x: (-x[0], x[1])); cand_n = cand_n[:15]
    cand_t.sort(key=lambda x: (-x[0], x[1])); cand_t = cand_t[:15]
    vat_vals = [v for _,_,v,_ in cand_t]

    def consistent(n,t,g):
        # harte Plausibilitäten
        if n is None or g is None: return False
        if not (Decimal("0") < n < g): return False
        if t is None: t = g - n
        if t < 0: return False
        # MwSt maximal ~30% von Brutto (mit kleiner Toleranz)
        if t > g * Decimal("0.30") + Decimal("0.20"): return False
        # Summe konsistent
        if abs(g - (n + t)) > Decimal("0.05"): return False
        return True

    best = (None, None, None, Decimal("1e9"))  # (n,t,g,score)
    for _, ig, g, lg in cand_g or [(0, N-1, None, "")]:
        if g is None: continue
        # Wenn keine Net-Kandidaten: aus g und t ableiten
        if not cand_n:
            nn = None
            for _, it, tt, lt in cand_t or [(0, N-1, None, "")]:
                if tt is None: continue
                n2 = g - tt
                if not consistent(n2, tt, g): continue
                # Score: Summe-Fehler + MwSt-Satz-Abstand + Nähe zu erkannter t
                rate_pen = Decimal("0")
                if n2 > 0:
                    try:
                        r = (tt/n2)*100
                        near = min(abs(r-x) for x in TYPICAL)
                        rate_pen = near
                        if vat_rate_inline is not None:
                            rate_pen = min(rate_pen, abs(r - vat_rate_inline))
                    except Exception:
                        pass
                t_match = min( (abs(tt - tv) for tv in vat_vals), default=Decimal("0.50") )
                score = Decimal("0")*Decimal("1000") + rate_pen + t_match
                if score < best[3]:
                    best = (n2.quantize(Decimal("0.01")), tt, g, score)
        # Mit Net-Kandidaten: n zuerst, t aus g-n
        for _, inx, n, ln in cand_n or [(0, N-1, None, "")]:
            if n is None: continue
            t2 = g - n
            if not consistent(n, t2, g): continue
            rate_pen = Decimal("0")
            try:
                r = (t2/n)*100
                near = min(abs(r-x) for x in TYPICAL)
                rate_pen = near
                if vat_rate_inline is not None:
                    rate_pen = min(rate_pen, abs(r - vat_rate_inline))
            except Exception:
                pass
            t_match = min( (abs(t2 - tv) for tv in vat_vals), default=Decimal("0.50") )
            score = Decimal("0")*Decimal("1000") + rate_pen + t_match
            if score < best[3]:
                best = (n, t2.quantize(Decimal("0.01")), g, score)

    n,v,g,_ = best
    if n is None or g is None:
        return None, None, None, vat_rate_inline

    # finaler Satz
    rate = None
    if n and v is not None and n > 0:
        try:
            rate = (v/n)*100
            rate = rate.quantize(Decimal("0.01"))
            if vat_rate_inline is not None and abs(rate - vat_rate_inline) > Decimal("1.0"):
                rate = vat_rate_inline
        except Exception:
            rate = vat_rate_inline
    else:
        rate = vat_rate_inline

    return n, v, g, rate

# ab jetzt aktiv:
find_amounts = find_amounts_v3
# --- end stricter amounts extractor v3 ---

# --- enforce integer rounding for VAT rate ---
def _round_rate_int(fn):
    def _w(text):
        n, t, g, rate = fn(text)
        from decimal import Decimal
        if isinstance(rate, Decimal):
            rate = rate.quantize(Decimal('1'))
        return n, t, g, rate
    return _w

find_amounts = _round_rate_int(find_amounts)
