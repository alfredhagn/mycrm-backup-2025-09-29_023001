#!/bin/bash

set -e

BASE="/srv/mycrm/timeclock"
TEMPLATES="$BASE/templates/timeclock"

echo "📁 Erstelle project_views.py..."
cat > "$BASE/project_views.py" << 'EOF'
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
EOF

echo "🔗 Erweitere urls.py..."

sed -i "/from . import views/a from . import project_views" "$BASE/urls.py"

sed -i '$ a\
urlpatterns += [\
    path("projects/", project_views.project_list, name="project_list"),\
    path("projects/new/", project_views.project_create, name="project_create"),\
    path("projects/<int:pk>/edit/", project_views.project_edit, name="project_edit"),\
    path("projects/<int:pk>/deactivate/", project_views.project_deactivate, name="project_deactivate"),\
]' "$BASE/urls.py"

echo "🖼️ Lege Templates an..."

mkdir -p "$TEMPLATES"

# Template: project_list.html
cat > "$TEMPLATES/project_list.html" << 'EOF'
{% extends "base.html" %}
{% block content %}
<h1>Projekte</h1>
<a href="{% url 'timeclock:project_create' %}">+ Neues Projekt</a>
<table>
  <tr>
    <th>Name</th><th>Aktiv?</th><th>Aktion</th>
  </tr>
  {% for p in projects %}
  <tr>
    <td>{{ p.name }}</td>
    <td>{{ p.is_active|yesno:"✅,❌" }}</td>
    <td>
      <a href="{% url 'timeclock:project_edit' p.pk %}">✏️</a>
      {% if p.is_active %}
        <a href="{% url 'timeclock:project_deactivate' p.pk %}">🗑</a>
      {% endif %}
    </td>
  </tr>
  {% endfor %}
</table>
{% endblock %}
EOF

# Template: project_form.html
cat > "$TEMPLATES/project_form.html" << 'EOF'
{% extends "base.html" %}
{% block content %}
<h1>{{ title }}</h1>
<form method="post">
  {% csrf_token %}
  <label for="name">Name:</label>
  <input type="text" name="name" value="{{ project.name|default:'' }}" required>
  {% if project %}
    <label>
      <input type="checkbox" name="is_active" {% if project.is_active %}checked{% endif %}>
      Aktiv
    </label>
  {% endif %}
  <br><br>
  <button type="submit">Speichern</button>
</form>
<a href="{% url 'timeclock:project_list' %}">Zurück zur Liste</a>
{% endblock %}
EOF

echo "✅ Projektverwaltung erfolgreich eingerichtet!"
