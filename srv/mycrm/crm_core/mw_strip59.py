import json, decimal, re
from django.utils.deprecation import MiddlewareMixin

# Whitespace- und Euro-Varianten
_WS   = r'(?:\s|\u00A0|\u202F|\u2009)*'
_EURO = r'(?:€|&euro;)'
# 59 mit Varianten: 59,00 | 59.00 | 59,-- | 59.- ; ggf. mit Spaces
_NUM59_TIGHT = r'59(?:[.,]\s*00|,--|-\.)?'.replace('-.', '-')
# Euro vor ODER nach der Zahl
_NUM59_SYM = rf'(?:{_EURO}{_WS})?{_NUM59_TIGHT}(?:{_WS}{_EURO})?'
# freistehender Token (keine Ziffern direkt angrenzt)
_NUM59_FREE = rf'(?<!\d){_WS}{_NUM59_SYM}{_WS}(?!\d)'

_RE_VALUE_Q   = re.compile(rf'(<input\b[^>]*\bname=["\'](Brutto|Netto|Betrag|Amount|Total|Summe)["\'][^>]*\bvalue=)\s*["\']\s*{_NUM59_SYM}\s*["\']', re.I)
_RE_VALUE_NOQ = re.compile(rf'(<input\b[^>]*\bname=["\'](Brutto|Netto|Betrag|Amount|Total|Summe)["\'][^>]*\bvalue=)\s*{_NUM59_SYM}\b', re.I)
_RE_PLACE_Q   = re.compile(rf'(<input\b[^>]*\bname=["\'](Brutto|Netto|Betrag|Amount|Total|Summe)["\'][^>]*\bplaceholder=)\s*["\']\s*{_NUM59_SYM}\s*["\']', re.I)

# data-sort="59,00" o. ä. leeren
_RE_DATA_SORT = re.compile(rf'(data-sort=)(["\']){_WS}{_NUM59_SYM}{_WS}\2', re.I)

def _is_59ish(val):
    try:
        if isinstance(val, (int, float, decimal.Decimal)):
            return abs(float(val) - 59.0) < 1e-9
        s = str(val).strip()
        s2 = (s.replace("€","")
               .replace("&euro;","")
               .replace("\u00A0"," ").replace("\u202F"," ").replace("\u2009"," ")
               .replace(" ",""))
        return s2 in {"59","59,00","59.00","59,--","59,-"}
    except Exception:
        return False

def _deep_clean(obj):
    if isinstance(obj, dict):
        return {k: _deep_clean(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_clean(v) for v in obj]
    return "" if _is_59ish(obj) else obj

# entfernt 59… zwischen > … < (auch verschachtelt), ohne HTML-Struktur zu zerstören
def _strip_between_tags(html: str) -> str:
    pat = re.compile(rf'>([^<>]*){_NUM59_SYM}([^<>]*)<', re.I)
    prev = None
    while prev != html:
        prev = html
        html = pat.sub(lambda m: '>' + (m.group(1) or '') + (m.group(2) or '') + '<', html)
    return html

class Strip59Middleware(MiddlewareMixin):
    def process_response(self, request, response):
        try:
            ct = response.get('Content-Type', '') or ''
            body = response.content

            # JSON: rekursiv neutralisieren
            if 'application/json' in ct:
                try:
                    data = json.loads(body.decode('utf-8', errors='ignore'))
                except Exception:
                    return response
                data = _deep_clean(data)
                new = json.dumps(data, ensure_ascii=False)
                response.content = new.encode('utf-8')
                response['Content-Length'] = str(len(response.content))
                return response

            # HTML: Form-Felder + harte Säuberung auf der Drafts-Seite
            if 'text/html' in ct:
                html = body.decode('utf-8', errors='ignore')

                # Form-Felder (value/placeholder) säubern
                html2 = _RE_VALUE_Q.sub(r'\1""', html)
                html2 = _RE_VALUE_NOQ.sub(r'\1""', html2)
                html2 = _RE_PLACE_Q.sub(r'\1""', html2)

                # Drafts-Liste: überall 59… tilgen (auch data-sort & zwischen Tags)
                if request.path.startswith('/crm/expenses/drafts'):
                    html3 = _RE_DATA_SORT.sub(r'\1\2\2', html2)     # data-sort=""
                    html3 = re.sub(_NUM59_FREE, '', html3, flags=re.I)
                    html3 = _strip_between_tags(html3)
                    if html3 != html:
                        response.content = html3.encode('utf-8')
                        response['Content-Length'] = str(len(response.content))
                        return response

                if html2 != html:
                    response.content = html2.encode('utf-8')
                    response['Content-Length'] = str(len(response.content))
                return response

            return response
        except Exception:
            return response
