from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project

@login_required
def project_list(request):
    projects = Project.objects.all().order_by("name")
    return render(request, "timeclock/project_list.html", {"projects": projects})

@login_required
def project_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        if name:
            project, created = Project.objects.get_or_create(name=name)
            if created:
                messages.success(request, "Projekt erstellt.")
            else:
                messages.info(request, "Projekt existiert bereits.")
            return redirect("timeclock:project_list")
        messages.error(request, "Name darf nicht leer sein.")
    return render(request, "timeclock/project_form.html", {"title": "Neues Projekt"})

@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        is_active = request.POST.get("is_active") == "on"
        if name:
            project.name = name
            project.is_active = is_active
            project.save()
            messages.success(request, "Projekt aktualisiert.")
            return redirect("timeclock:project_list")
        messages.error(request, "Name darf nicht leer sein.")
    return render(request, "timeclock/project_form.html", {
        "title": "Projekt bearbeiten",
        "project": project,
    })

@login_required
def project_deactivate(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.is_active = False
    project.save()
    messages.success(request, "Projekt deaktiviert.")
    return redirect("timeclock:project_list")
