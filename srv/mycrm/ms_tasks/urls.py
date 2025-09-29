# /srv/mycrm/ms_tasks/urls.py
from django.urls import path
from . import views

app_name = "ms_tasks"

urlpatterns = [
    path("tasks/", views.task_list_view, name="task_list"),
    path("tasks/<str:list_id>/<str:task_id>/update/", views.update_task_view, name="update_task"),
    path("tasks/<str:list_id>/<str:task_id>/edit/", views.edit_task_view, name="edit_task"),
    path("tasks/<str:list_id>/<str:task_id>/delete/", views.delete_task_view, name="delete_task"),
]