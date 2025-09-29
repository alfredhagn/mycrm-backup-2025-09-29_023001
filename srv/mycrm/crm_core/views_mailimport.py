from __future__ import annotations
import base64, io, re, datetime as _dt, html, traceback
from typing import Optional, Dict, Any, List
import requests
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
from django.shortcuts import render

def _session_token(sess) -> Optional[str]:
    for k in ("ms_access_token","access_token","graph_token","ms_token","graph_access_token","token"):
        v = sess.get(k)
        if isinstance(v, str) and len(v) > 100 and v.count(".") >= 2:
            return v
    for k in list(sess.keys()):
        v = sess.get(k)
        if isinstance(v, dict):
            for kk in ("access_token","token"):
                vv = v.get(kk)
                if isinstance(vv, str) and len(vv) > 100 and vv.count(".") >= 2:
                    return vv
    return None

def _gget(token: str, url: str, stream: bool=False):
    h = {"Authorization": f"Bearer {token}"}
    return requests.get(url, headers=h, stream=stream, timeout=20)

def _list_attachments(token: str, mid: str) -> List[Dict[str, Any]]:
    r = _gget(token, f"https://graph.microsoft.com/v1.0/me/messages/{mid}/attachments?$select=id,name,contentType,size,isInline")
    if r.status_code != 200:
        print("MAILIMPORT: list_attachments failed", r.status_code, (r.text or "")[:400])
        return []
    return r.json().get("value", []) or []

def _download_attachment_pdf(token: str, mid: str, aid: str) -> Optional[bytes]:
    r = _gget(token, f"https://graph.microsoft.com/v1.0/me/messages/{mid}/attachments/{aid}")
    if r.status_code == 200 and r.headers.get("Content-Type","").lower().startswith("application/json"):
        data = r.json()
        cbytes = data.get("contentBytes")
        if cbytes:
            try:
                raw = base64.b64decode(cbytes, validate=False)
                if raw:
                    return raw
            except Exception as ex:
                print("MAILIMPORT: base64 decode failed:", ex)
    rv = _gget(token, f"https://graph.microsoft.com/v1.0/me/messages/{mid}/attachments/{aid}/$value", stream=True)
    if rv.status_code == 200:
        return rv.content
    print("MAILIMPORT: download_attachment failed", r.status_code, rv.status_code if 'rv' in locals() else None)
    return None

def _get_message_meta(token: str, mid: str) -> Dict[str, Any]:
    r = _gget(token, f"https://graph.microsoft.com/v1.0/me/messages/{mid}?$select=subject,from,sender,receivedDateTime")
    if r.status_code == 200:
        return r.json()
    return {}

def _extract_text(pdf_bytes: bytes) -> str:
    try:
        from pdfminer.high_level import extract_text
        txt = extract_text(io.BytesIO(pdf_bytes))
        if txt and txt.strip():
            return txt
    except Exception as ex:
        print("MAILIMPORT: pdfminer extract failed:", ex)
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        parts = []
        for p in reader.pages:
            try:
                parts.append(p.extract_text() or "")
            except Exception:
                pass
        return "\n".join(parts)
    except Exception as ex:
        print("MAILIMPORT: PyPDF2 extract failed:", ex)
    return ""

def _norm_amount(s: str) -> float:
    s = s.replace("\xa0"," ").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(s)
    except Exception:
        return 0.0

def _parse_fields(txt: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    cand = re.findall(r'(?:EUR|€)?\s*([0-9]{1,3}(?:[.\s][0-9]{3})*(?:,[0-9]{2}))', txt, flags=re.I)
    amts = [_norm_amount(c) for c in cand]
    if amts:
        out["Brutto"] = f"{max(amts):.2f}"
    m = re.search(r'([0-3]?\d\.[01]?\d\.\d{4})', txt)
    if m:
        try:
            dt = _dt.datetime.strptime(m.group(1), "%d.%m.%Y").date()
            out["Datum"] = dt.isoformat()
        except Exception:
            out["Datum"] = m.group(1)
    m = re.search(r'(?:Rechnung(?:s)?nr\.?|Rechnungsnummer|Invoice\s*(?:No\.|Number)?)\s*[:#]?\s*([A-Za-z0-9\-\/\.]{3,})', txt, flags=re.I)
    if m:
        out["Rechnungsnummer"] = m.group(1)
    dfrom = ((meta.get("from") or {}).get("emailAddress") or {})
    name = (dfrom.get("name") or "").strip()
    addr = (dfrom.get("address") or "").strip()
    if name:
        out["Lieferant"] = name
    elif addr:
        out["Lieferant"] = addr.split("@")[0]
    return out

def from_email(request):
    # Früh loggen & Probe erlauben
    try:
        q = dict(request.GET.lists())
    except Exception:
        q = {k: [request.GET.get(k)] for k in request.GET.keys()}
    print("MAILIMPORT: hit", {k: (v[0] if isinstance(v, list) and v else v) for k,v in q.items()})

    if request.GET.get("probe") == "1":
        return HttpResponse("MAILIMPORT probe OK")

    try:
        mid = request.GET.get("mid") or request.GET.get("message_id")
        aid = request.GET.get("aid") or request.GET.get("attachment_id")
        pick = request.GET.get("pick")

        token = _session_token(request.session)
        if not token:
            print("MAILIMPORT: no token; session keys:", list(request.session.keys()))
            return HttpResponseNotFound("Kein Microsoft-Token in der Session (bitte neu anmelden).")

        if not mid:
            return HttpResponseBadRequest("Erwarte ?mid=... (Message-ID).")

        if pick:
            atts = _list_attachments(token, mid)
            pdfs = [a for a in atts if (a.get("contentType","").lower()=="application/pdf" or str(a.get("name","")).lower().endswith(".pdf"))]
            if not pdfs:
                return HttpResponseNotFound("Keine PDF-Anhänge gefunden.")
            html_items = []
            for a in pdfs:
                html_items.append(
                    f'<li>{html.escape(a.get("name","(ohne Name)"))} '
                    f'<a class="btn btn-sm btn-outline-success" '
                    f'href="/crm/invoices/draft/from-email/?mid={mid}&aid={a.get("id")}">Als Ausgabe vormerken</a>'
                    f'</li>'
                )
            return HttpResponse("<h3>PDF auswählen</h3><ul>" + "\n".join(html_items) + "</ul>")

        if not aid:
            return HttpResponseBadRequest("Erwarte ?aid=... (Attachment-ID) oder ?pick=1.")

        print(f"MAILIMPORT: start mid={mid[:12]}… aid={aid[:12]}…")
        pdf = _download_attachment_pdf(token, mid, aid)
        if not pdf:
            return HttpResponseNotFound("PDF-Download fehlgeschlagen.")

        text = _extract_text(pdf)
        print("MAILIMPORT: text_len=", len(text))
        meta = _get_message_meta(token, mid)
        parsed = _parse_fields(text or "", meta)
        print("MAILIMPORT: parsed=", parsed)

        # --- v3: Parser anwenden/ergänzen ---
        text = locals().get('text','')
        parsed = locals().get('parsed', {})
        try:
            _p3 = _mi_extract_amounts_v3(text)
            if _p3:
                if parsed:
                    parsed.update({k:v for k,v in _p3.items() if v})
                else:
                    parsed = _p3
            print("MAILIMPORT: parsed_v3=", parsed)
        except Exception as _ex:
            print("MAILIMPORT: parsed_v3 ERROR", _ex)

        ctx = {
            "item": {"Brutto": parsed.get("Brutto"), "Datum": parsed.get("Datum")},
            "parsed": parsed,
            "message_id": mid,
            "attachment_id": aid,
            "today": _dt.date.today().isoformat(),
        }
        ctx.setdefault("base_template","crm_core/base.html")
        # -- Mailimport: fehlende Keys in parsed auffüllen & Netto ggf. berechnen --
        try:
            _p = parsed if isinstance(parsed, dict) else {}
            def _num(_x):
                try:
                    return round(float(str(_x).replace(' ','').replace('.','').replace(',','.')), 2)
                except Exception:
                    return None
            _b = _num(_p.get('Brutto'))
            _n = _num(_p.get('Netto'))
            _ust = _p.get('USt') or _p.get('MwSt') or _p.get('VAT')
            _rate = None
            if isinstance(_ust,(int,float)):
                _rate = float(_ust)
            elif isinstance(_ust,str):
                _s = _ust.strip().replace('%','').replace(',','.')
                if _s:
                    try: _rate = float(_s)
                    except Exception: _rate = None
            if _n is None and _b is not None and _rate is not None:
                _n = round(_b/(1.0+(_rate/100.0)), 2)
                _p['Netto'] = f"{_n:.2f}"
            for _k in ('Brutto','Netto','USt','USt-Art','Rechnungsnummer','Lieferant','Datum','Zahlungsdatum','Kategorie'):
                _p.setdefault(_k, '')
            ctx['parsed'] = _p
        except Exception:
            pass

        # -- Mailimport: Beträge zuverlässig aus Text ermitteln (Solver) --
        try:
            _p = parsed if isinstance(parsed, dict) else {}
            # Textquelle
            def _normspace(t): 
                return " ".join((t or "").replace("\u00a0"," ").split())
            _txt = ""
            for _k in ("text","pdf_text","body_text","plain_text","full_text"):
                _v = locals().get(_k) if "_k" in locals() else None
                if not _v:
                    _v = ctx.get(_k) if isinstance(ctx, dict) else None
                if isinstance(_v, str) and _v.strip():
                    _txt = _v; break
            T = _normspace(_txt)
        
            import math
            AMT = r"(?:[0-9]{1,3}(?:[\\.,][0-9]{3})*[\\.,][0-9]{2})"
        
            def _find(label):
                m = re.search(rf"(?i){label}\\s*[:\\-]?\\s*({AMT})(?!\\s*%)", T)
                return m.group(1) if m else None
        
            brutto_s = _find(r"(?:gesamt\\s*)?brutto")
            netto_s  = _find(r"(?:gesamt\\s*)?netto")
            mvat = re.search(rf"(?i)(?:mwst|ust)[^0-9%]{{0,40}}([0-9]{{1,2}}(?:[\\.,][0-9]{{1,2}})?)\\s*%[^0-9]{{0,10}}({AMT})", T)
            rate_s = mvat.group(1) if mvat else None
            vat_s  = mvat.group(2) if mvat else None
        
            def _num(x):
                try:
                    xs=str(x).strip().replace(' ','')
                    if xs.count(',')==1 and xs.count('.')>=1:
                        xs=xs.replace('.','').replace(',','.')
                    elif xs.count(',')==1 and xs.count('.')==0:
                        xs=xs.replace(',','.')
                    return round(float(xs),2)
                except Exception:
                    return None
        
            # Werte-Kandidaten aus Text
            B = _num(brutto_s)
            N = _num(netto_s)
            R = _num(rate_s)    # Prozent (z.B. 20.00)
            V = _num(vat_s)     # USt-Betrag
        
            # Bestehende parsed-Werte berücksichtigen – aber später ggf. überschreiben
            def getp(k): 
                return _num(_p.get(k)) if _p.get(k) not in ('', None) else None
            if B is None: B = getp('Brutto')
            if N is None: N = getp('Netto')
            if R is None: R = getp('USt')
            if V is None: V = getp('USt-Betrag')
        
            # Solver: aus zwei Größen die anderen berechnen
            # Priorität: (N,R) -> (V,B), (B,R) -> (N,V), (N,V)->(B,R), (B,V)->(N,R)
            if N is not None and R is not None:
                V = round(N * R/100.0, 2)
                B = round(N + V, 2)
            elif B is not None and R is not None:
                N = round(B / (1.0 + R/100.0), 2)
                V = round(B - N, 2)
            elif N is not None and V is not None:
                B = round(N + V, 2)
                R = round((V / N) * 100.0, 2) if N not in (0,None) else R
            elif B is not None and V is not None:
                N = round(B - V, 2)
                R = round((V / N) * 100.0, 2) if N not in (0,None) else R
        
            # Notfalls: wenn "Brutto" fälschlich der Steuersatz (z.B. 20.00) war,
            # und wir nun N/V haben, setze B konsistent:
            if (B is None or (R is not None and abs(B - R) < 0.01)) and N is not None and (V is not None or R is not None):
                if V is None and R is not None:
                    V = round(N * R/100.0, 2)
                if V is not None:
                    B = round(N + V, 2)
        
            # Werte formatiert zurückschreiben (überschreiben inkonsistenter Altwerte)
            if B is not None: _p['Brutto'] = f"{B:.2f}"
            if N is not None: _p['Netto']  = f"{N:.2f}"
            if R is not None: _p['USt']    = f"{R:.2f}"
            if V is not None: _p['USt-Betrag'] = f"{V:.2f}"
        
            # USt-Art ableiten
            if R is not None and R > 0:
                _p.setdefault('USt-Art','Normal')
            else:
                _p.setdefault('USt-Art','Keine')
        
            # Fallbacks (auch für Template)
            for _k in ('Brutto','Netto','USt','USt-Art','Rechnungsnummer','Lieferant','Datum','Zahlungsdatum','Kategorie'):
                _p.setdefault(_k, '')
        
            # Kategorie-Notfall-Default
            if not _p.get('Kategorie'):
                _p['Kategorie'] = 'Sonstiges'
        
            ctx['parsed']=_p
            print("MAILIMPORT: normalized=", _p)
        except Exception as _ex:
            print("MAILIMPORT: normalize error:", _ex)
        


    except Exception as ex:
        tb = traceback.format_exc()
        print("MAILIMPORT: EXCEPTION\n", tb)
        body = f"<h3>MAILIMPORT Fehler</h3><pre>{html.escape(tb)}</pre>"
        return HttpResponse(body, status=500)


# === Mailimport: robuster Betrags-/MwSt-Parser (v3) ===
import re as _re
from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU

def _mi_normnum(x):
    if not x: return ''
    x = x.strip().replace('\u00a0',' ').replace(' ','')
    if ',' in x and '.' in x:
        x = x.replace('.','').replace(',','.')
    elif ',' in x:
        x = x.replace(',','.')
    try:
        q = _Dec(x).quantize(_Dec('0.01'), rounding=_RHU)
        return f"{q:.2f}"
    except:
        return ''

def _mi_extract_amounts_v3(text):
    T = text.replace('\u00a0',' ')
    AMT = r'([0-9]{1,3}(?:[.\s][0-9]{3})*(?:[,.][0-9]{2})|[0-9]+(?:[,.][0-9]{2}))'
    PC  = r'([0-9]{1,2}(?:[,.][0-9]{1,2})?)\s*%'

    def pick(lbls, near_amt=True, maxgap=80):
        for lb in lbls:
            if near_amt:
                m = _re.search(rf'{lb}[^0-9%]{{0,{maxgap}}}{AMT}', T, _re.I)
                if m: return _mi_normnum(m.group(1))
            else:
                m = _re.search(lb, T, _re.I)
                if m: return '1'
        return ''

    USt = ''; USt_B = ''
    m = _re.search(r'(mwst|umsatzsteuer|mehrwertsteuer|ust)[^0-9%]{0,40}'+PC+r'(?:[^0-9]{0,20}'+AMT+r')?', T, _re.I)
    if m:
        USt = _mi_normnum(m.group(2))
        if len(m.groups()) >= 3 and m.group(3):
            USt_B = _mi_normnum(m.group(3))

    Brutto = pick([r'gesamt\s*brutto', r'brutto\s*gesamt', r'bruttobetrag', r'betrag\s*brutto', r'gesamtbetrag\s*brutto'])
    Netto  = pick([r'gesamt\s*netto', r'netto\s*gesamt', r'nettobetrag', r'zwischensumme\s*netto', r'betrag\s*netto'])

    if not Brutto:
        m2 = _re.search(r'(gesamt|summe)[^0-9]{0,40}'+AMT+r'(?![^%]{0,10}%)', T, _re.I)
        if m2:
            Brutto = _mi_normnum(m2.group(2))

    if Brutto and USt and Brutto == USt:
        Brutto = ''

    Datum = ''
    m = _re.search(r'(?:(Rechnungsdatum|Datum)[^0-9]{0,12})(\d{1,2}\.\d{1,2}\.\d{2,4})', T, _re.I)
    if m:
        try:
            import datetime as _dt
            dd,mm,yy = m.group(2).split('.')
            yy = '20'+yy if len(yy)==2 else yy
            Datum = str(_dt.date(int(yy), int(mm), int(dd)))
        except: pass

    RNR = ''
    m = _re.search(r'(Rechnung(?:s)?nr\.?|Rechnungsnummer)[^A-Za-z0-9]{0,12}([A-Za-z0-9\-\/]+)', T, _re.I)
    if m: RNR = m.group(2).strip()

    Lieferant = ''
    m = _re.search(r'^\s*([A-Za-zÄÖÜäöü0-9\.\-\& ]{4,60}(?:Kundenservice|GmbH|AG|UG|KG|Ltd|S\.?A\.?R\.?L\.?)?)\s*$', T, _re.M)
    if m: Lieferant = m.group(1).strip()

    def D2(x):
        from decimal import Decimal as _Dec
        try: return _Dec(x or '0')
        except: return _Dec('0')

    if not Brutto and Netto and USt:
        from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
        Brutto = _mi_normnum( (D2(Netto) * (D2(USt)/_Dec('100') + _Dec('1'))).quantize(_Dec('0.01'), rounding=_RHU) )
    if not Netto and Brutto and USt:
        from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
        Netto = _mi_normnum( (D2(Brutto) / (D2(USt)/_Dec('100') + _Dec('1'))).quantize(_Dec('0.01'), rounding=_RHU) )
    if not USt_B and Brutto and Netto:
        from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
        USt_B = _mi_normnum( (D2(Brutto) - D2(Netto)).quantize(_Dec('0.01'), rounding=_RHU) )

    return {
        "Brutto": Brutto or "",
        "Netto": Netto or "",
        "USt": USt or "",
        "USt-Betrag": USt_B or "",
        "Datum": Datum or "",
        "Lieferant": Lieferant or "",
        "Rechnungsnummer": RNR or "",
    }
