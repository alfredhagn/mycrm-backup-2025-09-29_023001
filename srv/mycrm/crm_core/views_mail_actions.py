from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse, NoReverseMatch
import os
from urllib.parse import unquote

# Services aus der ms_tasks-App
from ms_tasks.services import get_task_lists
from ms_tasks.services import create_task as ms_create_task
from ms_tasks.ms_graph_client import MSGraphClient

# USER_ID wählen (wie in ms_tasks/views.py genutzt)
USER_ID = os.getenv("GRAPH_USER_ID") or os.getenv("GRAPH_DEFAULT_USER") or ""

def _safe_reverse(names, default="/"):
    for n in names:
        try: return reverse(n)
        except NoReverseMatch: pass
    return default

# TODO: Ersetze diese Dummy-Funktion durch deinen echten Graph-Helper:
def _get_message_subject(_user, message_id: str) -> str:
    return f"Mail {message_id}"

@login_required
def mail_to_task(request, message_id):
    try:
        # 1) aus Query-Param (vom Template mitgegeben)
        from urllib.parse import unquote
        qs_subj = request.GET.get("subject") or ""
        subject = unquote(qs_subj).strip() if qs_subj else ""

        # 2) falls leer: via Graph
        if not subject:
            subject = _get_message_subject_from_graph(message_id) or ""

        # 3) letzter Fallback
        if not subject:
            subject = f"Mail {message_id}"


        lists = get_task_lists(USER_ID) or []
        if not lists:
            messages.error(request, "Keine MS To Do-Listen gefunden.")
            return redirect(_safe_reverse(["ms_tasks:task_list"], "/msgraph/tasks/"))

        # Wunschliste wählen (erste als Fallback)
        preferred_name = (os.getenv("GRAPH_TODO_LIST_NAME") or "").lower()
        the_list = next((x for x in lists if x.get("displayName","").lower()==preferred_name), None) or lists[0]
        list_id = the_list.get("id")
        if not list_id:
            messages.error(request, "Konnte keine gültige Liste bestimmen.")
            return redirect(_safe_reverse(["ms_tasks:task_list"], "/msgraph/tasks/"))

        res = ms_create_task(
            USER_ID, list_id,
            title=subject,
            body="Automatisch aus E-Mail erstellt",
            due_date_iso=None,
            importance="normal",
        )
        rid = None
        if isinstance(res, dict):
            rid = res.get("id")
        elif isinstance(res, str):
            import json
            try: rid = (json.loads(res) or {}).get("id")
            except Exception: rid = None
        if rid:
            messages.success(request, f"Aufgabe angelegt: {subject}")
        else:
            messages.warning(request, "Task-Erstellung ohne ID-Rückgabe – bitte prüfen.")

        return redirect(_safe_reverse(["ms_tasks:task_list"], "/msgraph/tasks/"))
    except Exception as e:
        messages.error(request, f"Fehler bei MS To Do: {e}")
        return redirect(_safe_reverse(["ms_tasks:task_list"], "/msgraph/tasks/"))

# Die mail_to_expense-View kannst du vorerst as-is lassen; wir verdrahten sie später.

from django.utils import timezone  # falls noch nicht importiert
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import NoReverseMatch

@login_required
def mail_to_expense(request, message_id):
    from crm_core import models
    from django.contrib import messages
    # 1) Titel/Betreff aus Query
    subj_qs = request.GET.get("subject") or ""
    subject = unquote(subj_qs).strip() if subj_qs else ""
    if not subject:
        subject = f"Mail {message_id}"
    # 2) Optional: später Absender/Domain → supplier
    supplier = ""
    # 3) Draft anlegen
    try:
        draft = models.ExpenseDraft.objects.create(
            description=subject,
            supplier=supplier,
            category="",
            amount=None,
            message_id=message_id,
        )
        messages.success(request, f"Ausgabe-Entwurf angelegt (#{draft.id}): {subject}")
    except Exception as e:
        messages.error(request, f"Fehler beim Anlegen des Ausgabe-Entwurfs: {e}")
    # 4) Zur Entwurfs-Liste
    try:
        from django.urls import reverse
        return redirect(reverse("expenses_drafts"))
    except Exception:
        return redirect("/crm/expenses/drafts/")


# --- BEGIN hotfix: make "Vormerken" always create a draft ---
from django.shortcuts import redirect

def mail_to_expense(request, message_id):
    # Wir geben die Info über die Query weiter; draft_add erzeugt dann den Eintrag.
    return redirect(f"/crm/expenses/drafts/add/?from=mail&message_id={message_id}&raw_preview=Vormerkung%20aus%20Mail%20{message_id}")
# --- END hotfix ---
