from decimal import Decimal, ROUND_HALF_UP
import re

_DEC2 = Decimal("0.01")

def _q2(x: Decimal) -> Decimal:
    return x.quantize(_DEC2, rounding=ROUND_HALF_UP)

def _money(val) -> Decimal:
    """
    Robust: akzeptiert '1.234,56', '1 234,56', "1'234,56", '1234.56', '59,--', etc.
    Gibt Decimal(0.00) bei None/unlesbar zurück.
    """
    if val is None:
        return Decimal("0.00")
    s = str(val)
    # NBSP & typische Tausendertrenner raus
    s = s.replace("\u00A0", " ").replace(" ", "").replace("'", "").strip()
    # Wenn Komma UND Punkt vorkommen: Punkte als Tausender raus, Komma -> Punkt
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # sonst Komma als Dezimaltrenner erlauben
        s = s.replace(",", ".")
    # Nur Zahl extrahieren (inkl. optionalem Minus)
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return Decimal("0.00")
    try:
        return _q2(Decimal(m.group(0)))
    except Exception:
        return Decimal("0.00")

def _parse_rate(rate_raw) -> tuple[Decimal, str]:
    """
    Liefert (Prozentsatz als Decimal, Code-String).
    Akzeptiert: '20', '20%', '10', '13', '0', 'RC', 'reverse', ...
    """
    if rate_raw is None:
        return Decimal("20"), "20"
    r = str(rate_raw).strip().lower()
    if r in {"rc", "reverse", "reverse-charge"}:
        return Decimal("0"), "RC"
    # Zahl rausziehen
    m = re.search(r"\d+(?:[.,]\d+)?", r)
    if not m:
        return Decimal("20"), "20"
    p = Decimal(m.group(0).replace(",", "."))
    # auf typische AT-Sätze normalisieren (optional)
    if p in {Decimal("20"), Decimal("13"), Decimal("10"), Decimal("0")}:
        code = str(int(p)) if p != 0 else "0"
    else:
        code = str(p.normalize())
    return p, code

def _from_brutto(brutto: Decimal, rate_raw):
    p, code = _parse_rate(rate_raw)
    if code == "RC" or p == 0:
        netto = brutto
        ust = Decimal("0.00")
        return _q2(netto), _q2(ust), code
    factor = Decimal("1") + (p / Decimal("100"))
    netto = brutto / factor
    ust = brutto - netto
    return _q2(netto), _q2(ust), code

def _from_netto(netto: Decimal, rate_raw):
    p, code = _parse_rate(rate_raw)
    if code == "RC" or p == 0:
        brutto = netto
        ust = Decimal("0.00")
        return _q2(brutto), _q2(ust), code
    brutto = netto * (Decimal("1") + (p / Decimal("100")))
    ust = brutto - netto
    return _q2(brutto), _q2(ust), code

class AmountsMiddleware:
    """
    Greift für POSTs unter /crm/…:
    - Falls Brutto vorhanden (und Netto leer/0): Netto & USt aus Brutto+UStSatz.
    - Falls Netto vorhanden (und Brutto leer/0): Brutto & USt aus Netto+UStSatz.
    - Felder werden als 2-Nachkommastellen-Strings in request.POST geschrieben.
    Felder: Brutto, Netto, USt, UStSatz
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if request.method == "POST" and request.path.startswith("/crm/"):
                qd = request.POST
                # QueryDict ist immutable -> Kopie
                q = qd.copy()

                brutto_raw = q.get("Brutto")
                netto_raw  = q.get("Netto")
                rate_raw   = q.get("UStSatz") or q.get("UstSatz") or q.get("ustsatz") or "20"

                has_b = brutto_raw is not None and str(brutto_raw).strip() != ""
                has_n = netto_raw  is not None and str(netto_raw).strip()  != ""

                if has_b and (not has_n or _money(netto_raw) == Decimal("0.00")):
                    b = _money(brutto_raw)
                    n, u, code = _from_brutto(b, rate_raw)
                    q["Brutto"]  = f"{b:.2f}"
                    q["Netto"]   = f"{n:.2f}"
                    q["USt"]     = f"{u:.2f}"
                    q["UStSatz"] = code
                elif has_n and (not has_b or _money(brutto_raw) == Decimal("0.00")):
                    n = _money(netto_raw)
                    b, u, code = _from_netto(n, rate_raw)
                    q["Brutto"]  = f"{b:.2f}"
                    q["Netto"]   = f"{n:.2f}"
                    q["USt"]     = f"{u:.2f}"
                    q["UStSatz"] = code
                # leichtes Plausibilitäts-Update wenn beides da, aber inkonsistent (>1 Cent)
                elif has_b and has_n:
                    b = _money(brutto_raw)
                    n = _money(netto_raw)
                    p, code = _parse_rate(rate_raw)
                    if b - n - _q2(b - n) != 0:  # numerisch streng
                        # Brutto priorisieren
                        n2, u, code = _from_brutto(b, rate_raw)
                        q["Brutto"]  = f"{b:.2f}"
                        q["Netto"]   = f"{n2:.2f}"
                        q["USt"]     = f"{u:.2f}"
                        q["UStSatz"] = code

                request.POST = q  # ausgetauschte QueryDict einsetzen
        except Exception:
            # niemals 500er durch Middleware auslösen
            pass
        return self.get_response(request)
