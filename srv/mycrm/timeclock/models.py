from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    is_remote = models.BooleanField(default=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(null=True, blank=True)
    duration_s = models.IntegerField(null=True, blank=True)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_at"]

    def __str__(self):
        return f"{self.user} – {self.project} – {self.start_at:%Y-%m-%d %H:%M}"

    def stop(self, end_time=None):
        if not end_time:
            end_time = timezone.now()
        self.end_at = end_time
        # Dauer in Sekunden
        self.duration_s = int((self.end_at - self.start_at).total_seconds())
        self.save(update_fields=["end_at", "duration_s"])
