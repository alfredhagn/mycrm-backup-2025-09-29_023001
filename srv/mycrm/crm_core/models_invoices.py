
from django.db import models
from django.contrib.auth import get_user_model

class InvoiceDraft(models.Model):
    # Quelle
    source = models.CharField(max_length=20, default="mail")         # mail|upload|other
    source_message_id = models.CharField(max_length=255, blank=True)  # z.B. Graph-ID
    source_attachment_id = models.CharField(max_length=255, blank=True)
    attachment_sha256 = models.CharField(max_length=64, blank=True)

    # Datei
    pdf = models.FileField(upload_to="invoices/source/%Y/%m/", blank=True)

    # Extraktion
    issuer = models.CharField(max_length=255, blank=True)    # Rechnungsteller
    invoice_number = models.CharField(max_length=128, blank=True)
    invoice_date = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=8, default="EUR")

    net_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)   # z.B. 19.00
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    gross_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    raw_text = models.TextField(blank=True)      # für Nachvollziehbarkeit
    raw_json = models.JSONField(null=True, blank=True)

    status = models.CharField(max_length=20, default="draft")  # draft|ready|posted
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        indexes = [
            models.Index(fields=["source_message_id", "source_attachment_id"]),
            models.Index(fields=["attachment_sha256"]),
        ]
