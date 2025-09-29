# /mnt/data/mycrm_project/srv/mycrm/code/ms_tasks/services.py
from .ms_graph_client import MSGraphClient

def get_task_lists():
    client = MSGraphClient()
    return client.get("/me/todo/lists")["value"]

def get_tasks_from_list(list_id):
    client = MSGraphClient()
    return client.get(f"/me/todo/lists/{list_id}/tasks")["value"]

def update_task_status(list_id, task_id, is_completed):
    client = MSGraphClient()
    return client.patch(f"/me/todo/lists/{list_id}/tasks/{task_id}", {
        "status": "completed" if is_completed else "notStarted"
    })
