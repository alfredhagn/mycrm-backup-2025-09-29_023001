from pathlib import Path
from datetime import time, timedelta
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib import messages
import logging
logger = logging.getLogger(__name__)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone
import datetime
import requests
import datetime as _dtm
_dt = _dtm.datetime

try:
    # kann String, Dict mit access_token oder OAuth2Session liefern
    from .ms_tokens import get_ms_session  # type: ignore
except Exception:
    get_ms_session = None

def _extract_bearer(obj):
    """Gibt einen Bearer-Token-String zurück oder None."""
    if not obj:
        return None
    if isinstance(obj, str):
        return obj.strip() or None
    if isinstance(obj, dict):
        return obj.get("access_token") or obj.get("token") or None
    tok = getattr(obj, "token", None)
    if isinstance(tok, dict):
        return tok.get("access_token") or tok.get("token")
    return None

@login_required
def plan_links(request):
    """Heutige (oder via ?days=2) Termine mit Teams-Join-Links (read-only)."""
    events = []

    sess_or_token = None
    if get_ms_session:
        try:
            sess_or_token = get_ms_session(request)
        except Exception:
            sess_or_token = None

    # Datumsfenster
    start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    days = 1
    try:
        days = max(1, int(request.GET.get("days", "1")))
    except Exception:
        pass
    end = start + datetime.timedelta(days=days)
    start_iso = start.isoformat()
    end_iso = end.isoformat()

    url = (
        "https://graph.microsoft.com/v1.0/me/calendarView"
        f"?startDateTime={start_iso}&endDateTime={end_iso}&$top=50&$orderby=start/dateTime"
    )
    prefer_hdr = {'Prefer': 'outlook.timezone="Europe/Vienna"'}

    try:
        # OAuth2Session direkt nutzen
        if hasattr(sess_or_token, "get"):
            r = sess_or_token.get(url, headers=prefer_hdr, timeout=15)
        else:
            token = _extract_bearer(sess_or_token)
            if not token:
                return render(request, "print/plan_links.html", {"events": events})
            headers = {"Authorization": f"Bearer {token}", **prefer_hdr}
            r = requests.get(url, headers=headers, timeout=15)

        r.raise_for_status()
        data = r.json()
        for ev in data.get("value", []):
            online = ev.get("onlineMeeting") or {}
            link = online.get("joinUrl") or ev.get("onlineMeetingUrl")
            events.append({
                "subject": ev.get("subject") or "(ohne Betreff)",
                "start": (ev.get("start") or {}).get("dateTime"),
                "end": (ev.get("end") or {}).get("dateTime"),
                "location": (ev.get("location") or {}).get("displayName"),
                "link": link,
            })
    except Exception:
        # bewusst still – Seite bleibt leer statt 500
        pass

    return render(request, "print/plan_links.html", {"events": events})


from django.views.decorators.http import require_POST
from django.http import HttpResponse

def _tz():
    return timezone.get_current_timezone()

def _aware(dt: datetime) -> datetime:
    return timezone.make_aware(dt, _tz()) if timezone.is_naive(dt) else dt.astimezone(_tz())

def _iso_local(dt: datetime) -> str:
    return _aware(dt).isoformat()

def _day_range(day):
    start = _aware(_dt.combine(day, time(0,0,0)))
    end   = start + timedelta(days=1)
    return start, end

def _bearer_from_allauth(user):
    """Versuche den Microsoft-Access-Token aus django-allauth zu lesen."""
    try:
        from allauth.socialaccount.models import SocialToken, SocialAccount
        acc = SocialAccount.objects.filter(user=user, provider__in=["microsoft","azuread"]).first()
        if not acc:
            return None
        tok = SocialToken.objects.filter(account=acc).order_by("-id").first()
        if tok and getattr(tok, "token", None):
            return tok.token
    except Exception:
        pass
    return None

def _graph_bearer(user):
    # 1) Projekt-Helper
    try:
        from crm_core.ms_auth import get_ms_session
    except Exception:
        get_ms_session = None
    try:
        if get_ms_session:
            sess = get_ms_session(user)
            tok = getattr(sess, "token", None)
            if isinstance(tok, dict) and tok.get("access_token"):
                return tok["access_token"]
            if isinstance(sess, str) and sess.startswith("ey"):
                return sess
    except Exception:
        pass
    # 2) allauth SocialToken
    t = _bearer_from_allauth(user)
    if t:
        return t
    return None

def _fetch_tasks_for_day(day):
    tasks = []
    try:
        # App-Only Client (AZURE_* in ENV); nutzt /users/{id}/todo/*
        from ms_tasks.services import get_task_lists, get_tasks_from_list
        user_id = os.getenv("GRAPH_USER_ID") or None
        lists = get_task_lists(user_id) or []
        for lst in lists:
            lid = lst.get("id"); lname = lst.get("displayName") or "Tasks"
            items = get_tasks_from_list(user_id, lid) or []
            for t in items:
                if (t.get("status") or "").lower() == "completed":
                    continue
                due = ((t.get("dueDateTime") or {}).get("dateTime") or "")[:10]
                if not due or due == day.isoformat():
                    tasks.append({"title": t.get("title") or "(ohne Titel)", "where": lname})
    except Exception:
        pass
    return tasks[:50]

def _fetch_graph_events_safe(request, user, day):
    try:
        return _fetch_graph_events(user, day, request)
    except TypeError:
        try:
            return _fetch_graph_events(user, day)
        except Exception:
            return []
    except Exception:
        return []

def _fetch_tasks_for_day_safe(day):
    try:
        return _fetch_tasks_for_day(day)
    except Exception:
        return []

@require_POST
@login_required
def plan_save(request):
    try:
        day = timezone.localdate()
        events = _fetch_graph_events_safe(request, request.user, day) or []
        tasks  = _fetch_tasks_for_day_safe(day) or []
        ctx = {"day": day, "events": events, "tasks": tasks, "print_mode": True}
        html = render_to_string("print/plan.html", ctx)

        root = Path(getattr(settings, "FILES_ROOT", "/srv/mycrm/files"))
        target = root / "Zeitmanagement"
        target.mkdir(parents=True, exist_ok=True)
        ts = _dt.now().strftime("%Y-%m-%d_%H%M")
        fn = target / f"Plan_{day.isoformat()}_{ts}.html"
        fn.write_text(html, encoding="utf-8")

        messages.success(request, f"Tagesplan gespeichert: {fn.name}")
        return redirect("/crm/files/?p=Zeitmanagement")
    except Exception as e:
        logger.exception("plan_save fatal: %s", e)
        return redirect("/crm/plan/today/")

@login_required
def plan_today(request):
    """
    Tagesplan: Termine + Aufgaben + Teams-Links für den gewählten Tag (default = heute).
    """
    from datetime import datetime, date
    from django.utils import timezone
    # Datum aus Query (?date=YYYY-MM-DD), sonst lokales Heute
    qs = request.GET.get("date")
    if qs:
        try:
            day = datetime.fromisoformat(qs).date()
        except Exception:
            day = timezone.localdate()
    else:
        day = timezone.localdate()

    logger.warning("PLAN_TODAY TRACE before events day=%s", day)

    # Events
    events = []
    try:
        events = _fetch_graph_events(request.user, day, request)
    except Exception as ex:
        logger.exception("PLAN_TODAY events error: %s", ex)
        events = []

    logger.warning("PLAN_TODAY TRACE after events count=%s", len(events))

    # Tasks
    tasks = []
    try:
        tasks = _fetch_graph_tasks(request.user, request)
    except Exception as ex:
        logger.exception("PLAN_TODAY tasks error: %s", ex)
        tasks = []

    # Flag: gibt es Join-Links?
    try:
        any_link = any(bool(e.get("link")) for e in (events or []))
    except Exception:
        any_link = False

    ctx = {"day": day, "events": events, "tasks": tasks, "any_link": any_link}
    return render(request, "print/plan.html", ctx)

def plan_save(request):
    try:
        day = timezone.localdate()
        events = _fetch_graph_events_safe(request, request.user, day) or []
        tasks  = _fetch_tasks_for_day_safe(day) or []
        ctx = {"day": day, "events": events, "tasks": tasks, "print_mode": True}
        html = render_to_string("print/plan.html", ctx)

        root = Path(getattr(settings, "FILES_ROOT", "/srv/mycrm/files"))
        target = root / "Zeitmanagement"
        target.mkdir(parents=True, exist_ok=True)
        ts = _dt.now().strftime("%Y-%m-%d_%H%M")
        fn = target / f"Plan_{day.isoformat()}_{ts}.html"
        fn.write_text(html, encoding="utf-8")

        messages.success(request, f"Tagesplan gespeichert: {fn.name}")
        return redirect("/crm/files/?p=Zeitmanagement")
    except Exception as e:
        try:
            logger.exception("plan_save fatal: %s", e)
        except Exception:
            pass
        return redirect("/crm/plan/today/")


def _get_graph_bearer(request, user):
    # 1) Session-Token
    try:
        for k in ("access_token","ms_access_token","token","graph_access_token","socialaccount_token"):
            v = getattr(getattr(request, "session", {}), "get", lambda *_: None)(k)
            if isinstance(v, str) and len(v) > 80:
                logger.warning("PLAN_TODAY bearer_source=session:str")
                return v
            if isinstance(v, dict) and v.get("access_token"):
                logger.warning("PLAN_TODAY bearer_source=session:dict")
                return v["access_token"]
    except Exception:
        pass
    # 2) Allauth
    try:
        from allauth.socialaccount.models import SocialToken, SocialAccount
        acc = SocialAccount.objects.filter(user=user, provider__in=["microsoft","azuread","microsoft_graph","microsoftprovider"]).order_by("-id").first()
        if acc:
            tok = SocialToken.objects.filter(account=acc).order_by("-id").first()
            if tok and getattr(tok, "token", None):
                logger.warning("PLAN_TODAY bearer_source=allauth")
                return tok.token
    except Exception:
        pass
    # 3) Projekt-Helper
    try:
        from crm_core.ms_auth import get_ms_session
        sess = get_ms_session(user)
        t = getattr(sess, "token", None)
        if isinstance(t, dict) and t.get("access_token"):
            logger.warning("PLAN_TODAY bearer_source=ms_session:dict")
            return t["access_token"]
        if isinstance(sess, str) and sess.startswith("ey"):
            logger.warning("PLAN_TODAY bearer_source=ms_session:str")
            return sess
    except Exception:
        pass
    logger.warning("PLAN_TODAY bearer_source=none")
    return None


def _fetch_graph_tasks(user, request=None, include_lists=None):
    """
    Holt offene To-Do-Aufgaben aus Microsoft Graph (alle Listen, sofern include_lists=None).
    Rückgabe: Liste von Dicts mit title, due (iso oder "–"), status, priority, list, url.
    """
    import requests, logging
    logger = logging.getLogger(__name__)
    tasks = []

    # Bearer ermitteln – gleiche Logik wie bei Events
    def _get_graph_bearer(request, user):
        # 1) Session
        try:
            for k in ("access_token","ms_access_token","token","graph_access_token","socialaccount_token"):
                v = getattr(getattr(request, "session", {}), "get", lambda *_: None)(k)
                if isinstance(v, str) and len(v) > 80:
                    logger.warning("PLAN_TODAY TASK bearer_source=session:str")
                    return v
                if isinstance(v, dict) and v.get("access_token"):
                    logger.warning("PLAN_TODAY TASK bearer_source=session:dict")
                    return v["access_token"]
        except Exception:
            pass
        # 2) allauth
        try:
            from allauth.socialaccount.models import SocialToken, SocialAccount
            acc = SocialAccount.objects.filter(user=user, provider__in=["microsoft","azuread","microsoft_graph","microsoftprovider"]).order_by("-id").first()
            if acc:
                tok = SocialToken.objects.filter(account=acc).order_by("-id").first()
                if tok and getattr(tok, "token", None):
                    logger.warning("PLAN_TODAY TASK bearer_source=allauth")
                    return tok.token
        except Exception:
            pass
        # 3) Projekt-Helper
        try:
            from crm_core.ms_auth import get_ms_session
            sess = get_ms_session(user)
            t = getattr(sess, "token", None)
            if isinstance(t, dict) and t.get("access_token"):
                logger.warning("PLAN_TODAY TASK bearer_source=ms_session:dict")
                return t["access_token"]
            if isinstance(sess, str) and sess.startswith("ey"):
                logger.warning("PLAN_TODAY TASK bearer_source=ms_session:str")
                return sess
        except Exception:
            pass
        logger.warning("PLAN_TODAY TASK bearer_source=none")
        return None

    bearer = _get_graph_bearer(request, user) if request is not None else None
    if not bearer:
        logger.warning("PLAN_TODAY TASK has_token=False (early)")
        return tasks

    base = "https://graph.microsoft.com/v1.0/me/todo/lists"
    headers = {"Authorization": f"Bearer {bearer}", "Accept": "application/json"}
    try:
        lr = requests.get(base, headers=headers, timeout=20)
        if not lr.ok:
            logger.warning("PLAN_TODAY TASK lists_status=%s body=%s", lr.status_code, (lr.text or "")[:300])
            return tasks
        lists = (lr.json() or {}).get("value", [])
    except Exception as ex:
        logger.exception("PLAN_TODAY TASK lists_error: %s", ex)
        return tasks

    for lst in lists:
        lname = (lst.get("displayName") or "").strip()
        if include_lists and lname not in include_lists:
            continue
        lid = lst.get("id")
        if not lid:
            continue
        # Nur nicht-abgeschlossene Tasks
        url = f"https://graph.microsoft.com/v1.0/me/todo/lists/{lid}/tasks"
        params = {"$top":"100", "$orderby":"dueDateTime/dateTime"}
        try:
            tr = requests.get(url, headers=headers, params=params, timeout=20)
            if not tr.ok:
                logger.warning("PLAN_TODAY TASK list=%s tasks_status=%s body=%s", lname, tr.status_code, (tr.text or "")[:300])
                continue
            for t in (tr.json() or {}).get("value", []):
                status = (t.get("status") or "").strip()
                if status.lower() == "completed":
                    continue
                title = (t.get("title") or "(ohne Titel)").strip()
                due = "–"
                d = t.get("dueDateTime") or {}
                if d.get("dateTime"):
                    due = d["dateTime"] + (" " + (d.get("timeZone") or "")) if d.get("timeZone") else d["dateTime"]
                priority = {1:"high", 2:"normal", 3:"low"}.get(t.get("importance"), t.get("importance") or "normal")
                web = t.get("webLink") or ""
                tasks.append({"title": title, "due": due, "status": status or "notStarted", "priority": priority, "list": lname or "—", "url": web})
        except Exception as ex:
            logger.exception("PLAN_TODAY TASK fetch_error list=%s: %s", lname, ex)
            continue

    # Sortierung: (Fällig unbekannt am Ende), dann Datum, dann Priorität
    def _k(x):
        due = x.get("due","–")
        has_due = 0 if due and due != "–" else 1
        pr = {"high":0,"normal":1,"low":2}.get(str(x.get("priority")).lower(), 5)
        return (has_due, due, pr, x.get("title",""))
    tasks.sort(key=_k)
    return tasks


def _fetch_graph_events(user, day, request=None):
    import logging
    logging.getLogger(__name__).warning('PLAN_TODAY EV enter')
    import requests, logging, datetime as _dt
    from datetime import time, timedelta
    from django.utils import timezone
    logger = logging.getLogger(__name__)

    def _get_graph_bearer(request, user):
        # 1) Session
        try:
            for k in ("access_token","ms_access_token","token","graph_access_token","socialaccount_token"):
                v = getattr(getattr(request, "session", {}), "get", lambda *_: None)(k)
                if isinstance(v, str) and len(v) > 80:
                    logger.warning("PLAN_TODAY EV bearer_source=session:str"); return v
                if isinstance(v, dict) and v.get("access_token"):
                    logger.warning("PLAN_TODAY EV bearer_source=session:dict"); return v["access_token"]
        except Exception: pass
        # 2) allauth
        try:
            from allauth.socialaccount.models import SocialToken, SocialAccount
            acc = SocialAccount.objects.filter(user=user, provider__in=["microsoft","azuread","microsoft_graph","microsoftprovider"]).order_by("-id").first()
            if acc:
                tok = SocialToken.objects.filter(account=acc).order_by("-id").first()
                if tok and getattr(tok, "token", None):
                    logger.warning("PLAN_TODAY EV bearer_source=allauth"); return tok.token
        except Exception: pass
        # 3) Projekt-Helper
        try:
            from crm_core.ms_auth import get_ms_session
            sess = get_ms_session(user)
            t = getattr(sess, "token", None)
            if isinstance(t, dict) and t.get("access_token"):
                logger.warning("PLAN_TODAY EV bearer_source=ms_session:dict"); return t["access_token"]
            if isinstance(sess, str) and sess.startswith("ey"):
                logger.warning("PLAN_TODAY EV bearer_source=ms_session:str"); return sess
        except Exception: pass
        logger.warning("PLAN_TODAY EV bearer_source=none")
        return None

    bearer = _get_graph_bearer(request, user) if request is not None else None
    if not bearer:
        logger.warning("PLAN_TODAY EV has_token=False (early)")
        return []

    tz = timezone.get_current_timezone()
    # lokaler Tag -> UTC [startZ, endZ)
    start_local = timezone.make_aware(_dt.datetime.combine(day, time(0,0,0)), tz)
    end_local   = start_local + timedelta(days=1)
    start_utc   = start_local.astimezone(_dt.timezone.utc)
    end_utc     = end_local.astimezone(_dt.timezone.utc)
    z = lambda d: d.strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {
        "Authorization": f"Bearer {bearer}",
        "Accept": "application/json",
        'Prefer': 'outlook.timezone="W. Europe Standard Time"',
    }

    def _parse(values):
        out = []
        for ev in (values or [])[:200]:
            s = ev.get("start") or {}; e = ev.get("end") or {}
            sdt = (s.get("dateTime") or ""); edt = (e.get("dateTime") or "")
            title = ev.get("subject") or "(ohne Betreff)"
            where = (ev.get("location") or {}).get("displayName") or ""
            join = (ev.get("onlineMeeting") or {}).get("joinUrl") or ev.get("onlineMeetingUrl")
            if not join:
                bp = (ev.get("bodyPreview") or "")[:1000]
                import re as _re
                m = _re.search(r"https://teams\.microsoft\.com/[^\s<>'\"]+", bp)
                if m: join = m.group(0)
            try:
                t1 = _dt.datetime.fromisoformat(sdt.replace("Z","+00:00"))
                t2 = _dt.datetime.fromisoformat(edt.replace("Z","+00:00")) if edt else None
                t1 = t1.astimezone(tz); t2 = t2.astimezone(tz) if t2 else None
                tstr = t1.strftime("%H:%M") + (("–"+t2.strftime("%H:%M")) if t2 else "")
            except Exception:
                tstr = ""
            out.append({"title": title, "time": tstr, "where": where, "link": join, "web": ev.get("webLink")})
        out.sort(key=lambda e: (e.get("time","99:99")[:2], e.get("time","99:99")[3:5]))
        return out

    events = []
    # 1) calendarView
    try:
        params = {"startDateTime": z(start_utc), "endDateTime": z(end_utc),
                  "$select": "subject,bodyPreview,start,end,location,onlineMeeting,onlineMeetingUrl,webLink",
                  "$orderby": "start/dateTime", "$top": "100"}
        logger.warning("PLAN_TODAY EV window startZ=%s endZ=%s", params["startDateTime"], params["endDateTime"])
        r = requests.get("https://graph.microsoft.com/v1.0/me/calendarView", headers=headers, params=params, timeout=20)
        logger.warning("PLAN_TODAY EV calendarView status=%s url=%s", r.status_code, r.url)
        if r.ok:
            events = _parse((r.json() or {}).get("value"))
            logger.warning("PLAN_TODAY EV calendarView parsed=%d", len(events))
        else:
            logger.warning("PLAN_TODAY EV calendarView error=%s", (r.text or "")[:300])
    except Exception as ex:
        logger.exception("PLAN_TODAY EV calendarView http_error: %s", ex)

    # 2) Fallback: alle Kalender
    if not events:
        try:
            lr = requests.get("https://graph.microsoft.com/v1.0/me/calendars", headers=headers, timeout=20)
            logger.warning("PLAN_TODAY EV calendars status=%s", lr.status_code)
            if lr.ok:
                for cal in (lr.json() or {}).get("value", []):
                    cid = cal.get("id"); cname = (cal.get("name") or "").strip()
                    if not cid: continue
                    params = {"startDateTime": z(start_utc), "endDateTime": z(end_utc),
                              "$select": "subject,bodyPreview,start,end,location,onlineMeeting,onlineMeetingUrl,webLink",
                              "$orderby": "start/dateTime", "$top": "100"}
                    url = f"https://graph.microsoft.com/v1.0/me/calendars/{cid}/calendarView"
                    cr = requests.get(url, headers=headers, params=params, timeout=20)
                    logger.warning("PLAN_TODAY EV cal[%s] status=%s", cname or cid[:6], cr.status_code)
                    if cr.ok:
                        parsed = _parse((cr.json() or {}).get("value"))
                        logger.warning("PLAN_TODAY EV cal[%s] parsed=%d", cname or cid[:6], len(parsed))
                        events.extend(parsed)
                    else:
                        logger.warning("PLAN_TODAY EV cal[%s] error=%s", cname or cid[:6], (cr.text or "")[:200])
            else:
                logger.warning("PLAN_TODAY EV calendars error=%s", (lr.text or "")[:200])
        except Exception as ex:
            logger.exception("PLAN_TODAY EV calendars http_error: %s", ex)

    logger.warning("PLAN_TODAY EV total_events=%d", len(events))
    return events

