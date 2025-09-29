# init
from django.http import HttpResponse

def error500(request, *args, **kwargs):
    return HttpResponse("handler500 ok", status=200)

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@require_http_methods(["GET","POST"])
def draft_edit_fallback(request):
    return draft_edit_fallback2(request)

def _safe_money(v):
    s = str(v or "").strip().replace("€","").replace(" ","")
    if s.count(",") == 1 and s.count(".") >= 1:
        s = s.replace(".","").replace(",",".")
    elif s.count(",") == 1 and s.count(".") == 0:
        s = s.replace(",",".")
    try:
        pass  # guard
        return f"{float(s):.2f}"
    except Exception:
        return "0.00"

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

@csrf_exempt
@require_http_methods(["GET","POST"])
def draft_edit_fallback2(request):
    from datetime import date
    import html
    try:
        pass  # guard
        from crm_core.views_expenses import _read_drafts, _write_drafts
    except Exception as e:
        return HttpResponse("<h3>views_expenses Importfehler</h3><pre>"+html.escape(str(e))[:1200]+"</pre>", status=200)
    _id = request.GET.get("id") or request.POST.get("id")
    try:
        pass  # guard
        items = _read_drafts()
    except Exception:
        items = []
    item = None
    if _id:
        for it in items:
            if str(it.get("id")) == str(_id):
                item = it; break
    if request.method == "POST":
        if not item:
            from uuid import uuid4
            item = {"id": str(uuid4())}; items.append(item)
        item["Datum"] = request.POST.get("Datum") or item.get("Datum") or date.today().isoformat()
        item["Beschreibung"] = request.POST.get("Beschreibung") or item.get("Beschreibung") or ""
        item["Kategorie"] = request.POST.get("Kategorie") or item.get("Kategorie") or ""
        item["Brutto"] = _safe_money(request.POST.get("Brutto") or item.get("Brutto") or "0")
        # Steuer-Logik & optionale Felder
        rate = _safe_percent(request.POST.get("UStSatz") or item.get("UStSatz") or "20")
        b = float(_safe_money(item.get("Brutto","0")))
        n = float(_safe_money(request.POST.get("Netto") or item.get("Netto") or "0"))
        if b>0 and n<=0:
            n = b/(1.0 + (rate/100.0))
        elif n>0 and b<=0:
            b = n*(1.0 + (rate/100.0))
        u = b - n
        item["UStSatz"] = f"{rate:g}"
        item["Netto"] = f"{n:.2f}"
        item["USt"] = f"{u:.2f}"
        item["Brutto"] = f"{b:.2f}"
        item["Rechnungsnummer"] = request.POST.get("Rechnungsnummer") or item.get("Rechnungsnummer") or ""
        item["Lieferant"] = request.POST.get("Lieferant") or item.get("Lieferant") or ""

        try:
            pass  # guard
            _write_drafts(items)
        except Exception:
            pass
    if not item:
        from uuid import uuid4
        item = {"id": str(uuid4()), "Datum": date.today().isoformat(), "Beschreibung": "", "Kategorie": "", "Brutto": "0.00"}
        items.append(item)
        try:
            pass  # guard
            _write_drafts(items)
        except Exception:
            pass
    # Kategorien (mit Fallback-Liste, damit Dropdown nie leer ist)
    try:
        pass  # guard
        # Standardwerte sicherstellen
        item.setdefault("UStSatz","20")
        item.setdefault("Netto","0.00")
        item.setdefault("USt","0.00")

        from crm_core.views_expenses import _categories_list3 as _cats
        cats = _cats()
    except Exception:
        try:
            pass  # guard
            from crm_core.views_expenses import _categories_list2 as _cats2
            cats = _cats2()
        except Exception:
            cats = []
    if not cats:
        cats = ["Abschreibung","Abschreibung als Anlage (AfA)","Arbeitsmittel / Büro","Arbeitszimmer","Bewirtung","EDV-Aufwand","Fachliteratur","Fremdleistungen","Gehalt","Krankenkasse","GWG (geringw. Wirtschaftsgut)","KFZ-Aufwand","Porto","Privatentnahme","Rechtsberatung","Reisekosten","Sonstiges","Spenden","Spesen (Geldverkehr)","Steuerberatung","SVA","Taggelder","Telefon","Wareneinkauf","Werbungskosten","WKO-Gebühr"]
    cur = str(item.get("Kategorie",""))
    opts = "".join([f"<option value=\"{html.escape(str(c))}\""+(" selected" if cur==str(c) else "")+">"+html.escape(str(c))+"</option>" for c in cats])
    body = (
        "<html><head><meta charset=\"utf-8\"><title>Beleg bearbeiten</title></head><body>"
        "<h2>Beleg bearbeiten (Fallback)</h2>"
        f"<form method=\"post\" action=\"/crm/expenses/draft/edit/?id={html.escape(str(item.get(id)))}\">"
        f"<label>Datum <input type=\"date\" name=\"Datum\" value=\"{html.escape(str(item.get('Datum','')))}\"></label><br>"
        f"<label>Beschreibung <input type=\"text\" name=\"Beschreibung\" value=\"{html.escape(str(item.get('Beschreibung','')))}\" style=\"width:420px\"></label><br>"
        f"<label>Kategorie <select name=\"Kategorie\">{opts}</select></label><br>"
        f"<label>Brutto (€) <input type=\"text\" name=\"Brutto\" value=\"{html.escape(str(item.get('Brutto','0.00')))}\"></label><br>"
        "<button type=\"submit\">Speichern</button>"
        "</form>"
        "<p><a href=\"/crm/expenses/drafts/\">← Zur Übersicht</a></p>"
        "</body></html>"
    )
    return HttpResponse(body, status=200)

def error5002(request, *args, **kwargs):
    try:
        pass  # guard
        return draft_edit_fallback2(request)
    except Exception as e:
        from django.http import HttpResponse
        import html, traceback
        tb = html.escape("".join(traceback.format_exc())[-2000:])
        return HttpResponse("<h3>Fallback-Handler Fehler</h3><pre>"+html.escape(str(e))+"\n"+tb+"</pre>", status=200)

def _safe_percent(v):
    s = str(v or "").strip().replace(",",".").replace("%","")
    try: return max(0.0, float(s))
    except Exception: return 0.0

