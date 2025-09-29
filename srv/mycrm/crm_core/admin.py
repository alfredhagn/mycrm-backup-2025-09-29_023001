from django.contrib import admin
from .models import Company, Contact, EmailLog, DocumentLink
from django.core.exceptions import FieldDoesNotExist


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'website', 'created_at')


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'contact', 'recipient' , 'timestamp')
    list_filter = ('timestamp',)


@admin.register(DocumentLink)
class DocumentLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'company', 'contact')


# crm_core/admin.py
from django.contrib import admin
from django.core.exceptions import FieldDoesNotExist
from .models import Contact  # sicherstellen, dass es nur EINEN Import/Registrierung gibt

def _has_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
        return True
    except FieldDoesNotExist:
        return False

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Dynamische, fehlertolerante Admin-Liste für Contact.
    Nutzt die Felder, die es wirklich gibt – sonst fällt sie auf __str__ zurück.
    """

    # Liste der „Wunschfelder“ in sinnvoller Reihenfolge;
    # nur vorhandene Felder werden verwendet.
    _preferred = ["first_name", "last_name", "name", "email", "phone", "mobile", "company", "created_at"]

    def get_list_display(self, request):
        fields = [f for f in self._preferred if _has_field(self.model, f)]
        return tuple(fields) if fields else ("__str__",)

    def get_list_filter(self, request):
        candidates = []
        for fname in ("company", "created_at"):
            if _has_field(self.model, fname):
                candidates.append(fname)
        return tuple(candidates)

    def get_search_fields(self, request):
        # Suchfelder dynamisch, wenn vorhanden
        search_candidates = []
        for fname in ("first_name", "last_name", "name", "email", "phone", "mobile"):
            if _has_field(self.model, fname):
                search_candidates.append(fname)
        return tuple(search_candidates)

from .models import CallLog

@admin.register(CallLog)
class CallLogAdmin(admin.ModelAdmin):
    list_display = ("started_at", "direction", "number", "contact", "company", "status", "source", "duration_s")
    list_filter = ("source", "direction", "status")
    search_fields = ("number", "note")
    raw_id_fields = ("contact", "company")

from .models import ExpenseDraft

@admin.register(ExpenseDraft)
class ExpenseDraftAdmin(admin.ModelAdmin):
    list_display = ("id","date","amount","supplier","category","created_at")
    search_fields = ("description","supplier","category","message_id")
    list_filter = ("category","date","created_at")
