from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Contact(models.Model):
    # Bestehende Felder
    phone = models.CharField(max_length=64, blank=True)
    phone_normalized = models.CharField(max_length=32, blank=True, db_index=True)

    # Optionale Zusatzfelder (rückwärtskompatibel -> null/blank erlaubt)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name  = models.CharField(max_length=50, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)

    # Firma optional (bestehende Einträge haben evtl. keine Firma)
    company = models.ForeignKey(
        "crm_core.Company",
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    position   = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        # zuerst Name, dann Telefonnummer, sonst Fallback
        name = " ".join(filter(None, [getattr(self, "first_name", None), getattr(self, "last_name", None)])).strip()
        if name:
            return name
        phone = self.phone or self.phone_normalized
        return phone or f"Contact #{self.pk}"

    def save(self, *args, **kwargs):
        # Beispiel-Normalisierung (nur wenn du normalize_phone nutzt)
        try:
            from .utils import normalize_phone
            if self.phone and not self.phone_normalized:
                self.phone_normalized = normalize_phone(self.phone)
        except Exception:
            pass
        super().save(*args, **kwargs)

class EmailLog(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.EmailField(default='unknown@example.com')  # <-- hinzugefügt

   
    def __str__(self):
        return f"{self.subject} ({self.status})"

class DocumentLink(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

# crm_core/models.py
from django.db import models

class FileAsset(models.Model):
    file = models.FileField(upload_to="uploads/%Y/%m/%d")
    original_name = models.CharField(max_length=255, blank=True)
    size = models.BigIntegerField(default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    company = models.ForeignKey("Company", null=True, blank=True, on_delete=models.SET_NULL)
    contact = models.ForeignKey("Contact", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [models.Index(fields=["created_at", "original_name"])]

    @property
    def filename(self):
        import os
        # Basename aus dem gespeicherten Pfad (robust, falls file leer sein sollte)
        return os.path.basename(self.file.name or "")

    @property
    def display_name(self):
        # bevorzugt original_name; sonst Fallback auf Basename
        return self.original_name or self.filename

    def __str__(self):
        return self.display_name
# --- Call logging ----------------------------------------------------
from django.db import models

class CallLog(models.Model):
    DIRECTION_CHOICES = [
        ("in", "Eingehend"),
        ("out", "Ausgehend"),
        ("missed", "Verpasst"),
    ]
    STATUS_CHOICES = [
        ("initiated", "Gestartet"),
        ("ringing", "Klingelt"),
        ("answered", "Angenommen"),
        ("failed", "Fehlgeschlagen"),
        ("completed", "Beendet"),
    ]
    SOURCE_CHOICES = [
        ("sipgate", "Sipgate"),
        ("fritzbox", "Fritz!Box"),
        ("manual", "Manuell"),
    ]

    # Referenzen
    contact = models.ForeignKey('crm_core.Contact', on_delete=models.SET_NULL, null=True, blank=True, related_name='call_logs')
    company = models.ForeignKey('crm_core.Company', on_delete=models.SET_NULL, null=True, blank=True, related_name='call_logs')

    # Basisdaten
    number      = models.CharField(max_length=64, db_index=True)
    direction   = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    status      = models.CharField(max_length=12, choices=STATUS_CHOICES, default="initiated")
    source      = models.CharField(max_length=12, choices=SOURCE_CHOICES, default="sipgate")
    started_at  = models.DateTimeField(auto_now_add=True)
    duration_s  = models.PositiveIntegerField(null=True, blank=True)
    note        = models.TextField(blank=True)

    # Rohdaten der Quelle (z. B. Sipgate-JSON)
    raw         = models.JSONField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        who = self.contact or self.company or self.number
        return f"[{self.source}] {self.get_direction_display()} {self.number} – {self.get_status_display()} ({who})"

# --- Quick-Win: sehr einfaches Ausgaben-Entwurfsmodell ---
from django.db import models as _m

class ExpenseDraft(_m.Model):
    date        = _m.DateField(auto_now_add=True)
    amount      = _m.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = _m.TextField(blank=True, default="")
    supplier    = _m.CharField(max_length=255, blank=True, default="")
    category    = _m.CharField(max_length=100, blank=True, default="")
    message_id  = _m.CharField(max_length=255, blank=True, default="")

    created_at  = _m.DateTimeField(auto_now_add=True)

    def __str__(self):
        amt = f"{self.amount:.2f} €" if self.amount is not None else "—"
        return f"[{self.date}] {amt} {self.supplier} – {self.description[:60]}"
from .models_invoices import *
