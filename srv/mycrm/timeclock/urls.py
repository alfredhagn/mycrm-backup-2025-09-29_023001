from django.urls import path
from . import views

app_name = "timeclock"


urlpatterns = [
    path("projects/<int:pk>/delete/", views.project_delete, name="project_delete"),
    path("projects/<int:pk>/rename/", views.project_rename, name="project_rename"),
    path("projects/<int:pk>/toggle/", views.project_toggle, name="project_toggle"),
    path("projects/new/", views.project_new, name="project_new"),
    path("", views.time_dashboard, name="dashboard"),
    path("start/", views.time_start, name="start"),
    path("stop/", views.time_stop, name="stop"),
    path("new/", views.time_new, name="new"),
    path("export/", views.time_export, name="export"),
    path("export/form/", views.time_export_form, name="export_form"),
    path("export/file/", views.time_export, name="export_file"),
    path("edit/<int:pk>/", views.time_edit, name="edit"),
    path("delete/<int:pk>/", views.time_delete, name="delete"),
    path("projects/", views.project_list, name="project_list"),
]
