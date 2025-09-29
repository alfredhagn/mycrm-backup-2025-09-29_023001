# crm_core/services/fritzbox.py
import os, csv, ssl
from datetime import datetime
from django.conf import settings

def _direction_from_type(t: str) -> str:
    t = (t or "").strip().lower()
    if t in ("3", "out", "outgoing"): return "Ausgehend"
    if t in ("2", "missed", "verpasst"): return "Verpasst"
    return "Eingehend"

def _parse_duration(cells):
    # finde z.B. 0:02:31
    for cell in cells:
        if isinstance(cell, str) and cell.count(":") == 2 and cell[0].isdigit():
            return cell
    return ""

def _parse_date(s: str) -> str:
    s = (s or "").strip()
    for fmt in ("%d.%m.%y %H:%M", "%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    return s

# --- XML Parser (TR-064) --------------------------------------------------
def _et_text(elem, *names):
    for n in names:
        if elem is None: break
        child = elem.find(n)
        if child is not None and child.text is not None:
            return child.text
    return ""

def _parse_tr64_xml(xml_text: str, limit=None):
    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml_text)
    items = []
    for call in root.findall(".//Call"):
        t = _et_text(call, "Type", "type")
        direction = _direction_from_type(t)
        date = _parse_date(_et_text(call, "Date", "date"))
        duration = _et_text(call, "Duration", "duration")
        caller = _et_text(call, "Caller", "caller") or _et_text(call, "CallerNumber", "caller_number")
        callee = _et_text(call, "Called", "called") or _et_text(call, "CalledNumber", "called_number")
        items.append({
            "timestamp": date,
            "direction": direction,
            "caller": caller,
            "callee": callee,
            "duration": duration,
        })
        if limit and len(items) >= limit:
            break
    return items

# --- TR-064 fetch ---------------------------------------------------------
def _get_call_list_tr64(limit=None):
    host = getattr(settings, "FRITZBOX_HOST", None)
    user = getattr(settings, "FRITZBOX_USER", None)
    password = getattr(settings, "FRITZBOX_PASSWORD", None)
    timeout = int(getattr(settings, "FRITZBOX_TIMEOUT", 5))
    if not (host and user and password):
        raise RuntimeError("TR-064 nicht konfiguriert (FRITZBOX_HOST/USER/PASSWORD).")

    # optional: fritzconnection nutzen um URL zu erhalten
    try:
        from fritzconnection import FritzConnection
        fc = FritzConnection(address=host, user=user, password=password, timeout=timeout)
        # Manche Boxen haben Servicenamen mit oder ohne :1
        try:
            res = fc.call_action("X_AVM-DE_OnTel:1", "GetCallList")
        except Exception:
            res = fc.call_action("X_AVM-DE_OnTel", "GetCallList")
        url = res.get("NewCallListURL") or res.get("NewX_AVM-DE_CallListURL") or res.get("NewCallList")
        if not url:
            raise RuntimeError("TR-064: Keine CallList-URL erhalten.")
    except Exception as e:
        raise RuntimeError(f"TR-064 Init-Fehler: {e}")

    # URL auf XML erzwingen
    if "xml=" not in url:
        url = f"{url}{'&' if '?' in url else '?'}xml=1"

    # Abruf (selbstsigniertes Zertifikat tolerieren)
    import requests
    try:
        resp = requests.get(url, auth=(user, password), timeout=20, verify=False)
        if resp.status_code != 200:
            raise RuntimeError(f"TR-064 Abruf fehlgeschlagen (HTTP {resp.status_code})")
        return _parse_tr64_xml(resp.text, limit=limit)
    except Exception as e:
        raise RuntimeError(f"TR-064 Abruffehler: {e}")

# --- CSV Fallback ---------------------------------------------------------
def _candidate_paths(custom_path=None):
    base = getattr(settings, "BASE_DIR", os.getcwd())
    cands = []
    if custom_path:
        cands.append(custom_path)
    cands.append(getattr(settings, "FRITZBOX_CALLLIST_PATH", None))
    cands += [
        "/root/calllist.csv",
        os.path.join(base, "calllist.csv"),
        os.path.join(base, "data", "calllist.csv"),
        os.path.join(base, "var", "calllist.csv"),
    ]
    return [p for p in cands if p]

def _get_call_list_csv(path=None, limit=None):
    tried = []
    file_path = None
    for p in _candidate_paths(path):
        tried.append(p)
        if os.path.exists(p):
            file_path = p
            break
    if not file_path:
        raise RuntimeError("CSV nicht gefunden. Probierte Pfade: " + ", ".join(tried))

    items = []
    with open(file_path, "r", encoding="latin-1", errors="ignore") as f:
        r = csv.reader(f, delimiter=";")
        header = next(r, None)
        for row in r:
            if not row or len(row) < 5:
                continue
            kind = (row[0] or "").lower()
            direction = "Eingehend"
            if "ausgehend" in kind or "out" in kind: direction = "Ausgehend"
            if "verpasst" in kind or "missed" in kind: direction = "Verpasst"

            ts_val = _parse_date(row[1] if len(row) > 1 else "")
            dur = _parse_duration(row)

            items.append({
                "timestamp": ts_val,
                "direction": direction,
                "caller": row[2] if len(row)>2 and row[2] else (row[3] if len(row)>3 else ""),
                "callee": row[4] if len(row)>4 else "",
                "duration": dur,
            })
            if limit and len(items) >= limit:
                break
    return items

# --- Public API -----------------------------------------------------------
def get_call_list(path=None, limit=None):
    # 1) TR-064 wenn konfiguriert
    try:
        return _get_call_list_tr64(limit=limit)
    except Exception as e:
        tr64_err = str(e)
    # 2) CSV Fallback
    try:
        return _get_call_list_csv(path=path, limit=limit)
    except Exception as e:
        csv_err = str(e)
        raise RuntimeError(f"{tr64_err} | {csv_err}")