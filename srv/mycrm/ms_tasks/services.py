from __future__ import annotations

# Minimal-kompatible Services für Microsoft To Do via Graph
# - /me Fallback, wenn user_id leer ist
# - nutzt MSGraphClient._request(...) für POST/PATCH/DELETE (falls .post/.patch/.delete fehlen)

from .ms_graph_client import MSGraphClient

def _user_prefix(user_id: str | None) -> str:
    return f"/users/{user_id}" if user_id else "/me"

def _post(client: MSGraphClient, url: str, json: dict):
    if hasattr(client, "post"):
        return client.post(url, json)
    return client._request("POST", url, json=json)

def _patch(client: MSGraphClient, url: str, json: dict):
    if hasattr(client, "patch"):
        return client.patch(url, json)
    return client._request("PATCH", url, json=json)

def _delete(client: MSGraphClient, url: str):
    if hasattr(client, "delete"):
        return client.delete(url)
    return client._request("DELETE", url)

# --------- Lists ---------
def get_task_lists(user_id: str | None = None):
    client = MSGraphClient()
    return client.get(_user_prefix(user_id) + "/todo/lists") or []

# --------- Tasks in List ---------
def get_tasks(user_id: str | None, list_id: str):
    if not list_id:
        return []
    client = MSGraphClient()
    return client.get(_user_prefix(user_id) + f"/todo/lists/{list_id}/tasks") or []

def create_task(user_id: str | None, list_id: str, title: str, body: str | None = None,
                due_date_iso: str | None = None, importance: str = "normal"):
    client = MSGraphClient()
    payload = {
        "title": title,
        "importance": importance,
    }
    if body:
        payload["body"] = {"content": body, "contentType": "text"}
    if due_date_iso:
        payload["dueDateTime"] = {"dateTime": due_date_iso, "timeZone": "UTC"}
    return _post(client, _user_prefix(user_id) + f"/todo/lists/{list_id}/tasks", payload)

def update_task(user_id: str | None, list_id: str, task_id: str, **fields):
    client = MSGraphClient()
    # Felder wie {"status":"completed"} oder {"importance":"high"} etc.
    return _patch(client, _user_prefix(user_id) + f"/todo/lists/{list_id}/tasks/{task_id}", fields)

def delete_task(user_id: str | None, list_id: str, task_id: str):
    client = MSGraphClient()
    return _delete(client, _user_prefix(user_id) + f"/todo/lists/{list_id}/tasks/{task_id}")

# --- COMPAT WRAPPERS (für alte Importe in ms_tasks/views.py) ---

def get_tasks_from_list(user_id, list_id):
    """Kompatibilitätsalias für alte Importe."""
    return get_tasks(user_id, list_id)

# Optionale weitere Wrapper – nur falls deine Views sie importieren:
def update_task_in_list(user_id, list_id, task_id, **fields):
    """Alias auf update_task (falls früher anders benannt)."""
    return update_task(user_id, list_id, task_id, **fields)

def delete_task_from_list(user_id, list_id, task_id):
    """Alias auf delete_task (falls früher anders benannt)."""
    return delete_task(user_id, list_id, task_id)

# --- COMPAT WRAPPERS (erwartet von älteren Views) ---

def update_task_status(user_id, list_id, task_id, is_completed=True):
    """
    Kompatibilität: setzt den Status einer Aufgabe.
    is_completed: bool oder str ('completed'/'notStarted'/'inProgress')
    """
    status = is_completed
    if isinstance(is_completed, str):
        s = is_completed.lower()
        if s in ("completed","done","erledigt"): status = "completed"
        elif s in ("inprogress","in_progress"):   status = "inProgress"
        else:                                     status = "notStarted"
    else:
        status = "completed" if is_completed else "notStarted"
    return update_task(user_id, list_id, task_id, status=status)

def get_task_detail(user_id, list_id, task_id):
    """Alias: Task-Detail abrufen."""
    client = MSGraphClient()
    return client.get(_user_prefix(user_id) + f"/todo/lists/{list_id}/tasks/{task_id}") or {}

def get_list_detail(user_id, list_id):
    """Alias: Listen-Detail abrufen."""
    client = MSGraphClient()
    return client.get(_user_prefix(user_id) + f"/todo/lists/{list_id}") or {}

def get_tasks_from_list(user_id, list_id):
    """Alias auf get_tasks (bereits definiert)."""
    return get_tasks(user_id, list_id)

def update_task_in_list(user_id, list_id, task_id, **fields):
    """Alias auf update_task."""
    return update_task(user_id, list_id, task_id, **fields)

def delete_task_from_list(user_id, list_id, task_id):
    """Alias auf delete_task."""
    return delete_task(user_id, list_id, task_id)

# --- COMPAT WRAPPER: erwartet von ms_tasks/views.py ---
def update_task_fields(user_id, list_id, task_id, **fields):
    """Alias auf update_task – setzt beliebige Felder der Aufgabe."""
    return update_task(user_id, list_id, task_id, **fields)

# --- PATCH: JSON-Normalisierung für alle Graph-Antworten ---
import json

def _as_json(obj):
    """Konvertiert String -> dict/list; None -> {}; dict/list bleibt."""
    if obj is None:
        return {}
    if isinstance(obj, (dict, list)):
        return obj
    if isinstance(obj, (bytes, bytearray)):
        try:
            return json.loads(obj.decode("utf-8", "ignore"))
        except Exception:
            return {}
    if isinstance(obj, str):
        try:
            return json.loads(obj)
        except Exception:
            return {}
    # Unbekannter Typ
    return {}

def _as_list(resp):
    """
    Liefert IMMER eine Liste:
    - dict mit 'value' (Graph-typisch) -> value-Liste
    - list -> wie sie ist
    - sonst -> []
    """
    data = _as_json(resp)
    if isinstance(data, dict) and isinstance(data.get("value"), list):
        return data["value"]
    if isinstance(data, list):
        return data
    return []

# Ersetze Kernfunktionen so, dass sie _as_list/_as_json benutzen
def get_task_lists(user_id: str | None = None):
    client = MSGraphClient()
    return _as_list(client.get(_user_prefix(user_id) + "/todo/lists"))

def get_tasks(user_id: str | None, list_id: str):
    if not list_id:
        return []
    client = MSGraphClient()
    return _as_list(client.get(_user_prefix(user_id) + f"/todo/lists/{list_id}/tasks"))

def create_task(user_id: str | None, list_id: str, title: str, body: str | None = None,
                due_date_iso: str | None = None, importance: str = "normal"):
    client = MSGraphClient()
    payload = {"title": title, "importance": importance}
    if body:
        payload["body"] = {"content": body, "contentType": "text"}
    if due_date_iso:
        payload["dueDateTime"] = {"dateTime": due_date_iso, "timeZone": "UTC"}
    resp = _post(client, _user_prefix(user_id) + f"/todo/lists/{list_id}/tasks", payload)
    return _as_json(resp)
