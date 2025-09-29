from collections import defaultdict
from datetime import datetime, date, time, timedelta

import csv
import io
import logging
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Project, TimeEntry

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _get_default_project():
    proj, _ = Project.objects.get_or_create(name="Allgemein", defaults={"is_active": True})
    return proj

def _get_running_entry(user):
    return (
        TimeEntry.objects.filter(user=user, end_at__isnull=True)
        .order_by("-start_at")
        .first()
    )

def _redirect_or_json(request, ok_message, fallback_name="timeclock:dashboard"):
    next_url = request.POST.get("next")
    if next_url:
        messages.success(request, ok_message)
        return redirect(next_url)
    messages.success(request, ok_message)
    return redirect(fallback_name)

def _parse_date_any(s: str, default: date | None = None) -> date:
    """
    Akzeptiert: 01.09.2025, 2025-09-01, 2025.09.01, 1.9.2025
    und liefert datetime.date. Bei Fehler → default oder ValueError.
    """
    s = (s or "").strip()
    if not s:
        if default is not None:
            return default
        raise ValueError("Leeres Datum")

    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y.%m.%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass

    m = re.fullmatch(r"(\d{1,2})[.\-](\d{1,2})[.\-](\d{4})", s)
    if m:
        d, mth, y = map(int, m.groups())
        return date(y, mth, d)

    if default is not None:
        return default
    raise ValueError(f"Unbekanntes Datumsformat: {s!r}")

def _parse_time_hhmm(s: str) -> time:
    return datetime.strptime(s, "%H:%M").time()

def _minutes_ceil_to_30(total_minutes: int) -> int:
    return ((total_minutes + 29) // 30) * 30

def _tz():
    return timezone.get_current_timezone()

def _aware(dt: datetime) -> datetime:
    return timezone.make_aware(dt, _tz()) if timezone.is_naive(dt) else dt.astimezone(_tz())

def _day_range(d: date) -> tuple[datetime, datetime]:
    start = _aware(datetime.combine(d, time(0, 0, 0)))
    end   = _aware(datetime.combine(d + timedelta(days=1), time(0, 0, 0)))
    return start, end  # [start, end)

# -----------------------------------------------------------------------------
# Dashboard
# -----------------------------------------------------------------------------

@login_required
def time_dashboard(request):
    running = _get_running_entry(request.user)

    # letzte 50 Einträge (abgeschlossen zuerst)
    entries_qs = (
        TimeEntry.objects.filter(user=request.user)
        .order_by("-start_at")[:50]
    )

    entries = []
    for e in entries_qs:
        # Dauer (Minuten) robust berechnen
        if e.duration_s is not None:
            minutes = max(0, int(e.duration_s // 60))
        elif e.end_at:
            minutes = max(0, int(((e.end_at - e.start_at).total_seconds()) // 60))
        else:
            minutes = max(0, int(((timezone.now() - e.start_at).total_seconds()) // 60))

        entries.append({
            "id": e.id,
            "project": e.project.name if e.project_id else "",
            "place": "Remote" if e.is_remote else "Vor Ort",
            "start": e.start_at,
            "start_at": e.start_at,
            "end": e.end_at,
            "end_at": e.end_at,
            "duration": minutes,
            "duration_min": minutes,
            "note": e.note or "",
        })

    projects = Project.objects.filter(is_active=True).order_by("name")

    return render(request, "timeclock/dashboard.html", {
        "running": running,
        "entries": entries,
        "projects": projects,
    })

from django.views.decorators.http import require_http_methods  # falls noch nicht oben importiert

@login_required
def project_list(request):
    # Hotfix: solange es kein eigenes Projekt-Listing gibt, zurück zum Dashboard
    return redirect("timeclock:dashboard")


# -----------------------------------------------------------------------------
# Timer Start/Stop
# -----------------------------------------------------------------------------

@login_required
@require_POST
def time_start(request):
    # Projekt kann per ID (Dropdown) oder per Name (manuelle Eingabe) kommen
    project_id = request.POST.get("project")
    project_name = (request.POST.get("project_name") or "").strip()
    note = (request.POST.get("note") or "").strip()
    is_remote = request.POST.get("is_remote") in ("1", "true", "on", "yes")

    if _get_running_entry(request.user):
        messages.warning(request, "Es läuft bereits ein Timer.")
        return redirect("timeclock:dashboard")

    project = None
    if project_id:
        project = get_object_or_404(Project, pk=project_id)
    elif project_name:
        project, _ = Project.objects.get_or_create(name=project_name, defaults={"is_active": True})
    else:
        project = _get_default_project()

    TimeEntry.objects.create(
        user=request.user,
        project=project,
        is_remote=is_remote,
        start_at=timezone.now(),
        note=note,
    )
    return _redirect_or_json(request, "Timer gestartet.")

@login_required
@require_POST
def time_stop(request):
    running = _get_running_entry(request.user)
    if not running:
        messages.info(request, "Kein laufender Timer.")
        return redirect("timeclock:dashboard")

    running.end_at = timezone.now()
    # duration_s wird im Model.save() berechnet – zur Sicherheit hier ebenfalls:
    running.duration_s = int((running.end_at - running.start_at).total_seconds())
    running.save()

    return _redirect_or_json(request, "Timer gestoppt.")

@login_required
@require_POST
def time_delete(request, pk: int):
    entry = get_object_or_404(TimeEntry, pk=pk, user=request.user)
    entry.delete()
    messages.success(request, "Eintrag gelöscht.")
    return redirect("timeclock:dashboard")


# -----------------------------------------------------------------------------
# Manuelle Erfassung
# -----------------------------------------------------------------------------

@login_required
def time_new(request):
    if request.method == "GET":
        projects = Project.objects.filter(is_active=True).order_by("name")
        return render(request, "timeclock/new.html", {"projects": projects})

    # POST
    try:
        date_str = request.POST.get("date")  # optional; bei leer → heute
        d = _parse_date_any(date_str, default=timezone.localdate())

        start_t = _parse_time_hhmm(request.POST.get("start_time"))
        end_t   = _parse_time_hhmm(request.POST.get("end_time"))

        start_dt = _aware(datetime.combine(d, start_t))
        end_dt   = _aware(datetime.combine(d, end_t))
        if end_dt <= start_dt:
            raise ValueError("Ende muss nach Start liegen.")

        project_name = (request.POST.get("project_name") or "").strip()
        note = (request.POST.get("note") or "").strip()
        is_remote = request.POST.get("is_remote") in ("1", "true", "on", "yes")

        if project_name:
            project, _ = Project.objects.get_or_create(name=project_name, defaults={"is_active": True})
        else:
            project = _get_default_project()

        TimeEntry.objects.create(
            user=request.user,
            project=project,
            is_remote=is_remote,
            start_at=start_dt,
            end_at=end_dt,
            note=note,
            duration_s=int((end_dt - start_dt).total_seconds()),
        )
    except Exception as e:
        logger.exception("Fehler bei manueller Erfassung: %s", e)
        messages.error(request, f"Fehler: {e}")
        projects = Project.objects.filter(is_active=True).order_by("name")
        return render(request, "timeclock/new.html", {"projects": projects})

    return _redirect_or_json(request, "Eintrag gespeichert.")

from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET", "POST"])
def time_edit(request, pk: int):
    entry = get_object_or_404(TimeEntry, pk=pk, user=request.user)

    if request.method == "GET":
        # Defaults fürs Formular (HTML <input type="datetime-local"> erwartet ISO)
        tz = _tz()
        start_local = entry.start_at.astimezone(tz)
        end_local = entry.end_at.astimezone(tz) if entry.end_at else None

        projects = Project.objects.filter(is_active=True).order_by("name")
        return render(request, "timeclock/edit.html", {
            "entry": entry,
            "projects": projects,
            "start_iso": start_local.strftime("%Y-%m-%dT%H:%M"),
            "end_iso": end_local.strftime("%Y-%m-%dT%H:%M") if end_local else "",
        })

    # POST: Daten übernehmen
    try:
        project_id = request.POST.get("project")
        project_name = (request.POST.get("project_name") or "").strip()
        note = (request.POST.get("note") or "").strip()
        is_remote = request.POST.get("is_remote") in ("1", "true", "on", "yes")

        # Datum/Uhrzeit kommen als ISO von <input type="datetime-local">: YYYY-MM-DDTHH:MM
        start_raw = request.POST.get("start_at")
        end_raw = request.POST.get("end_at")  # optional

        if not start_raw:
            raise ValueError("Startzeit fehlt.")

        start_dt = _aware(datetime.strptime(start_raw, "%Y-%m-%dT%H:%M"))
        end_dt = None
        if end_raw:
            end_dt = _aware(datetime.strptime(end_raw, "%Y-%m-%dT%H:%M"))
            if end_dt <= start_dt:
                raise ValueError("Ende muss nach Start liegen.")

        # Projekt ermitteln
        if project_id:
            project = get_object_or_404(Project, pk=project_id)
        elif project_name:
            project, _ = Project.objects.get_or_create(name=project_name, defaults={"is_active": True})
        else:
            project = _get_default_project()

        # Speichern
        entry.project = project
        entry.is_remote = is_remote
        entry.start_at = start_dt
        entry.end_at = end_dt
        entry.note = note

        if end_dt:
            entry.duration_s = int((end_dt - start_dt).total_seconds())
        else:
            entry.duration_s = None  # noch laufend

        entry.save()
        messages.success(request, "Eintrag aktualisiert.")
        return redirect("timeclock:dashboard")
    except Exception as e:
        logger.exception("Fehler beim Editieren: %s", e)
        messages.error(request, f"Fehler: {e}")
        projects = Project.objects.filter(is_active=True).order_by("name")
        # alte Werte wieder einsetzen
        return render(request, "timeclock/edit.html", {
            "entry": entry,
            "projects": projects,
            "start_iso": request.POST.get("start_at") or "",
            "end_iso": request.POST.get("end_at") or "",
        })



# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------

@login_required
def time_export_form(request):
    # <input type="date"> erwartet ISO-Strings
    today = timezone.localdate()
    first = today.replace(day=1)
    return render(request, "timeclock/export_form.html", {
        "date_from": first.strftime("%Y-%m-%d"),
        "date_to":   today.strftime("%Y-%m-%d"),
    })

@login_required
def time_export(request):
    """
    Export: pro Tag genau 1 Zeile:
    Datum | Remote (h) | Vor Ort (h) | Gesamt (h, 0.5h aufgerundet) | Bemerkungen
    - akzeptiert DD.MM.YYYY, YYYY-MM-DD und YYYY.MM.DD als Eingabe
    - gruppiert nach *lokalem* Datum (Django-Zeitzone)
    """
    try:
        date_from = _parse_date_any(request.POST.get("date_from"))
        date_to   = _parse_date_any(request.POST.get("date_to"))
    except ValueError as e:
        messages.error(request, f"Ungültiges Datum: {e}")
        return render(request, "timeclock/export_form.html", {
            "date_from": request.POST.get("date_from") or "",
            "date_to":   request.POST.get("date_to") or "",
        })

    if date_from > date_to:
        messages.error(request, "Der Zeitraum ist ungültig: 'Von' liegt nach 'Bis'.")
        return render(request, "timeclock/export_form.html", {
            "date_from": date_from.strftime("%Y-%m-%d"),
            "date_to":   date_to.strftime("%Y-%m-%d"),
        })

    start_dt, _ = _day_range(date_from)
    _, end_dt   = _day_range(date_to)

    qs = (
        TimeEntry.objects
        .filter(start_at__gte=start_dt, start_at__lt=end_dt, user=request.user)
        .select_related("project")
        .order_by("start_at")
    )

    tz = _tz()
    by_day = defaultdict(lambda: {"Remote": 0, "Vor Ort": 0, "notes": []})

    for e in qs:
        # lokales Datum bestimmen
        start_local = e.start_at.astimezone(tz)
        d = start_local.date()

        # Dauer in Minuten robust
        if e.duration_s is not None:
            dur_min = max(0, int(e.duration_s // 60))
        elif e.end_at:
            dur_min = max(0, int(((e.end_at - e.start_at).total_seconds()) // 60))
        else:
            dur_min = max(0, int(((timezone.now() - e.start_at).total_seconds()) // 60))

        key = "Remote" if e.is_remote else "Vor Ort"
        by_day[d][key] += dur_min

        if e.note:
            note = e.note.strip()
            if note:
                by_day[d]["notes"].append(note)

    # Zeilen generieren
    rows = []
    for d in sorted(by_day.keys()):
        remote_min = by_day[d]["Remote"]
        onsite_min = by_day[d]["Vor Ort"]
        total_min  = remote_min + onsite_min

        rounded_total_min = _minutes_ceil_to_30(total_min)

        # Doppelte Notizen entfernen, Reihenfolge behalten
        seen, ordered_notes = set(), []
        for n in by_day[d]["notes"]:
            if n not in seen:
                seen.add(n)
                ordered_notes.append(n)
        notes = ", ".join(ordered_notes)

        rows.append((
            d.strftime("%d.%m.%Y"),
            round(remote_min / 60, 2),
            round(onsite_min / 60, 2),
            round(rounded_total_min / 60, 2),
            notes,
        ))

    fmt = (request.POST.get("format") or "xlsx").lower()

    if fmt == "csv":
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
        writer.writerow(["Datum", "Remote (h)", "Vor Ort (h)", "Gesamt (h, 0.5↑)", "Bemerkungen"])
        for r in rows:
            writer.writerow(r)
        resp = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = (
            f'attachment; filename="zeiterfassung_{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}.csv"'
        )
        return resp
    # --- Moduswahl: daily (bestehend) vs detailed (neu) -----------------------
    mode = (request.POST.get("mode") or request.GET.get("mode") or "daily").lower()
    if mode == "detailed":
        # Einzelne Zeilen: Datum, Start, Ende, Dauer (h), Ort, Projekt, Bemerkung
        entries_qs = TimeEntry.objects.filter(
            start_at__gte=_aware(datetime.combine(date_from, time(0,0))),
            start_at__lt=_aware(datetime.combine(date_to + timedelta(days=1), time(0,0)))
        ).order_by("start_at")
        rows_d = []
        for e in entries_qs:
            if not e.end_at or not e.duration_s:
                dur_h = ((e.end_at or timezone.now()) - e.start_at).total_seconds()/3600.0
            else:
                dur_h = e.duration_s/3600.0
            rows_d.append((
                e.start_at.astimezone(_tz()).strftime("%Y-%m-%d"),
                e.start_at.astimezone(_tz()).strftime("%H:%M"),
                (e.end_at.astimezone(_tz()).strftime("%H:%M") if e.end_at else ""),
                round(dur_h, 2),
                ("Remote" if e.is_remote else "Vor Ort"),
                (e.project.name if e.project_id else ""),
                (e.note or "")
            ))
        fmt = (request.POST.get("format") or "xlsx").lower()
        if fmt == "csv":
            buffer = io.StringIO(); writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
            writer.writerow(["Datum","Start","Ende","Dauer (h)","Ort","Projekt","Bemerkung"])
            for r in rows_d: writer.writerow(r)
            resp = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = f'attachment; filename="zeiterfassung_detailed_{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}.csv"'
            return resp
        try:
            import openpyxl
            wb = openpyxl.Workbook(); ws = wb.active; ws.title = "Einzeleinträge"
            ws.append(["Datum","Start","Ende","Dauer (h)","Ort","Projekt","Bemerkung"])
            for r in rows_d: ws.append(list(r))
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            wb.save(tmp.name); tmp.flush(); tmp.seek(0); data = tmp.read(); tmp.close()
            resp = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            resp["Content-Disposition"] = f'attachment; filename="zeiterfassung_detailed_{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}.xlsx"'
            return resp
        except Exception:
            # Fallback CSV
            buffer = io.StringIO(); writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
            writer.writerow(["Datum","Start","Ende","Dauer (h)","Ort","Projekt","Bemerkung"])
            for r in rows_d: writer.writerow(r)
            resp = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
            resp["Content-Disposition"] = f'attachment; filename="zeiterfassung_detailed_{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}.csv"'
            return resp



    # XLSX
    try:
        import openpyxl  # nur hier importieren, falls Paket fehlt → CSV als Fallback s.u.
    except Exception as e:
        logger.warning("openpyxl fehlt (%s) – weiche auf CSV aus.", e)
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";", lineterminator="\n")
        writer.writerow(["Datum", "Remote (h)", "Vor Ort (h)", "Gesamt (h, 0.5↑)", "Bemerkungen"])
        for r in rows:
            writer.writerow(r)
        resp = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
        resp["Content-Disposition"] = (
            f'attachment; filename="zeiterfassung_{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}.csv"'
        )
        return resp

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Zeiterfassung"
    ws.append(["Datum", "Remote (h)", "Vor Ort (h)", "Gesamt (h, 0.5↑)", "Bemerkungen"])
    for r in rows:
        ws.append(list(r))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    resp = HttpResponse(
        output.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    resp["Content-Disposition"] = (
        f'attachment; filename="zeiterfassung_{date_from.strftime("%Y-%m-%d")}_{date_to.strftime("%Y-%m-%d")}.xlsx"'
    )
    return resp
# --- Project management views ---
from django.db import IntegrityError
from django.db.models import Count
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["GET"])
def project_list(request):
    projects = (Project.objects
                .all()
                .annotate(entry_count=Count("timeentry"))
                .order_by("-is_active", "name"))
    return render(request, "timeclock/projects.html", {"projects": projects})

@login_required
@require_POST
def project_new(request):
    name = (request.POST.get("name") or "").strip()
    if not name:
        messages.error(request, "Bitte einen Projektnamen angeben.")
        return redirect("timeclock:project_list")
    try:
        Project.objects.create(name=name, is_active=True)
        messages.success(request, f'Projekt „{name}“ angelegt.')
    except IntegrityError:
        messages.warning(request, f'Projekt „{name}“ existiert bereits.')
    return redirect("timeclock:project_list")

@login_required
@require_POST
def project_toggle(request, pk: int):
    p = get_object_or_404(Project, pk=pk)
    p.is_active = not p.is_active
    p.save(update_fields=["is_active"])
    state = "aktiviert" if p.is_active else "deaktiviert"
    messages.success(request, f'Projekt „{p.name}“ {state}.')
    return redirect("timeclock:project_list")

@login_required
@require_POST
def project_rename(request, pk: int):
    p = get_object_or_404(Project, pk=pk)
    new_name = (request.POST.get("name") or "").strip()
    if not new_name:
        messages.error(request, "Neuer Name darf nicht leer sein.")
        return redirect("timeclock:project_list")
    if new_name == p.name:
        messages.info(request, "Name unverändert.")
        return redirect("timeclock:project_list")
    try:
        p.name = new_name
        p.save(update_fields=["name"])
        messages.success(request, f'Projekt umbenannt in „{new_name}“.')
    except IntegrityError:
        messages.warning(request, f'Projekt „{new_name}“ existiert bereits.')
    return redirect("timeclock:project_list")

@login_required
@require_POST
def project_delete(request, pk: int):
    p = get_object_or_404(Project, pk=pk)
    if TimeEntry.objects.filter(project=p).exists():
        messages.error(request, "Projekt hat Zeiteinträge und kann nicht gelöscht werden.")
        return redirect("timeclock:project_list")
    name = p.name
    p.delete()
    messages.success(request, f'Projekt „{name}“ gelöscht.')
    return redirect("timeclock:project_list")
# --- end project management views ---
