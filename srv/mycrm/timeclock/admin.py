from django.contrib import admin
from .models import Project, TimeEntry

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ("project", "user", "start_at", "end_at", "duration_s", "is_remote")
    list_filter = ("project", "is_remote")
    search_fields = ("note",)
