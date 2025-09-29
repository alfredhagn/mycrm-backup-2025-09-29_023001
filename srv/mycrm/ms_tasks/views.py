from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from .services import (
    get_task_lists, get_tasks_from_list,
    update_task_status, update_task_fields, delete_task
)

import logging, os

# User aus ENV (Fallback bleibt dein Account)
USER_ID = os.getenv("GRAPH_USER_ID", "alfred.hagn@hagninterim.de")

# Logging (optional)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
if not logger.handlers:
    try:
        handler = logging.FileHandler('/tmp/ms_tasks_error.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    except Exception:
        pass


def task_list_view(request):
    try:
        lists = get_task_lists(USER_ID)
        all_tasks = []
        for l in lists:
            tasks = get_tasks_from_list(USER_ID, l["id"])
            all_tasks.append({
                "list": l["displayName"],
                "tasks": tasks,
                "list_id": l["id"]
            })

        # Auswahl-Listen für Template (Django-Template kann kein .split())
        status_choices = ["notStarted", "inProgress", "completed", "waitingOnOthers", "deferred"]
        priority_choices = ["low", "normal", "high"]

        return render(
            request,
            "ms_tasks/tasks.html",
            {
                "task_data": all_tasks,
                "STATUSES": status_choices,
                "PRIORITIES": priority_choices,
            }
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def _redirect_or_json(request, ok_message: str):
    """Hilfsfunktion: Wenn 'next' in POST -> redirect + Message,
    sonst JSON {'status':'ok'} (für XHR)."""
    next_url = request.POST.get("next")
    if next_url:
        messages.success(request, ok_message)
        return redirect(next_url)
    return JsonResponse({"status": "ok"})


def update_task_view(request, list_id, task_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    is_completed = request.POST.get("completed") == "true"
    try:
        update_task_status(USER_ID, list_id, task_id, is_completed)
        return _redirect_or_json(request, "Aufgabe aktualisiert.")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def edit_task_view(request, list_id, task_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        payload = {}
        title = request.POST.get("title", "").strip()
        if title:
            payload["title"] = title

        body = request.POST.get("body", "").strip()
        if body:
            payload["body"] = {"contentType": "text", "content": body}

        status = request.POST.get("status", "").strip()
        if status in {"notStarted", "inProgress", "completed", "waitingOnOthers", "deferred"}:
            payload["status"] = status

        importance = request.POST.get("importance", "").strip()
        if importance in {"low", "normal", "high"}:
            payload["importance"] = importance

        due_date = request.POST.get("due_date", "").strip()  # yyyy-mm-dd
        if due_date:
            payload["dueDateTime"] = {
                "dateTime": f"{due_date}T00:00:00",
                "timeZone": "UTC"
            }

        if not payload:
            return JsonResponse({"error": "Keine Änderungen übermittelt."}, status=400)

        update_task_fields(USER_ID, list_id, task_id, **payload)
        return _redirect_or_json(request, "Aufgabe gespeichert.")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def delete_task_view(request, list_id, task_id):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    try:
        delete_task(USER_ID, list_id, task_id)
        return _redirect_or_json(request, "Aufgabe gelöscht.")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
