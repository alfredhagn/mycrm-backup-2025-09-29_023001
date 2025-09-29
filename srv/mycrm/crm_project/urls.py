from crm_core import views_safe as safe_views
from crm_project import ocr_views
def invoices_draft_from_email(request, *args, **kwargs):
    from django.shortcuts import redirect
    p = request.GET.copy()
    return redirect("/crm/expenses/ocr/from-email/?" + p.urlencode())

from django.urls import re_path
# ==== Local OCR bridge helper (top) ====
def attachments_ocr_get(request, *args, **kwargs):
    from django.shortcuts import redirect
    p = request.GET.copy()
    mid = p.get("mid") or p.get("message_id") or p.get("messageId") or p.get("id")
    aid = p.get("aid") or p.get("attachment_id") or p.get("attachmentId")
    if mid: p["mid"] = mid
    if aid: p["aid"] = aid
    p["ocr"] = "1"
    return redirect("/crm/invoices/draft/from-email/?" + p.urlencode())
# ==== /Local OCR bridge helper ====

from crm_core import views_expenses as exp_views
from crm_project import ocr_views
from crm_core import views_expenses as expenses_views
from crm_project import ocr_views
from django.contrib import admin
from django.urls import path, re_path, re_path, include, re_path
from django.views.generic import RedirectView

from crm_core import views_expenses as vexp
from crm_project import ocr_views
from crm_core import views_planner as vplan
from crm_project import ocr_views
from crm_core import views_download
from crm_project import ocr_views
from crm_core import views_files as files_views
from crm_project import ocr_views
from crm_core import views_mail_actions as vmail
from crm_project import ocr_views
from crm_core import views_onedrive as onedrive_views
from crm_project import ocr_views
from msgraph import views_actions as inbox_actions

urlpatterns = [
    path("crm/inbox/attachment/save", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    path("crm/inbox/attachment/save-invoice", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/save-invoice/?$", ocr_views.attachments_save_invoice, name="attachments_save_invoice_catchall"),
    # --- BEGIN CRM EXPORT ROUTES ---
    path("crm/expenses/drafts/export.xlsx", exp_views.drafts_export_xlsx, name="drafts_export"),
    path("crm/expenses/drafts/export", exp_views.drafts_export_xlsx),
    path("crm/expenses/export.xlsx", exp_views.drafts_export_xlsx),
    path("crm/expenses/export", exp_views.drafts_export_xlsx),
    # --- END CRM EXPORT ROUTES ---
        # Export der Ausgaben-Entwürfe (mehrere Schreibweisen kompatibel)
    path("crm/expenses/draft/edit/", safe_views.draft_edit_fallback2),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/expenses/ocr/from-email/", exp_views.ocr_from_email, name="ocr_from_email"),
    path("crm/invoices/draft/from-email/", invoices_draft_from_email, name="invoices_draft_from_email"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/inbox/attachment/ocr", attachments_ocr_get, name="attachment_ocr"),
    path("crm/inbox/attachment/ocr/", attachments_ocr_get),
    # --- Expenses Drafts: explizite, stabile Routen ---
    path("crm/expenses/drafts/", vexp.drafts_list, name="expenses_drafts"),
    path("crm/expenses/drafts/add/", vexp.draft_add, name="expenses_draft_add"),
    path("crm/expenses/drafts/edit/", vexp.draft_edit, name="draft_edit"),
    path("crm/expenses/drafts/update/", vexp.draft_update, name="draft_update"),



    # --- Mail-Actions ---
    path("crm/mail/<str:message_id>/to-task/", vmail.mail_to_task, name="mail_to_task"),
    path("crm/mail/<str:message_id>/to-expense/", vmail.mail_to_expense, name="mail_to_expense"),

    # --- Planner / Files ---
    path("crm/plan/save/", vplan.plan_save, name="plan_save"),
    path("crm/plan/today/", vplan.plan_today, name="plan_today"),
    path("crm/files/view/", views_download.view_file, name="files_view"),
    path("crm/files/download/", views_download.download_file, name="files_download"),
    path("crm/files/delete/", files_views.delete, name="files_delete"),
    path("crm/files/upload/", files_views.upload, name="files_upload"),
    path("crm/files/mkdir/", files_views.mkdir, name="files_mkdir"),
    path("crm/files/", files_views.index, name="files_index"),

    # --- Inbox / OneDrive ---
    path("crm/inbox/attachments/save/", inbox_actions.inbox_save_attachments, name="inbox_save_attachments"),
    path("crm/inbox/delete/", inbox_actions.inbox_delete, name="inbox_delete"),
    path("crm/onedrive/", onedrive_views.onedrive_browser, name="onedrive_browser"),
    path("crm/onedrive/mkdir/", onedrive_views.onedrive_mkdir, name="onedrive_mkdir"),
    path("crm/onedrive/upload/", onedrive_views.onedrive_upload, name="onedrive_upload"),
    path("crm/onedrive/download/<str:item_id>/", onedrive_views.onedrive_download, name="onedrive_download"),
    path("crm/onedrive/share/<str:item_id>/", onedrive_views.onedrive_share, name="onedrive_share"),

    # --- Restliche App-URLs ---
    path("crm/", include("crm_core.urls_invoices")),
    path("crm/", include("crm_core.urls_health")),
    path("crm/", include("crm_core.urls_tiles")),
    path("crm/", include("crm_core.urls_planner")),
    path("crm/", include("crm_core.urls")),
    path("crm/time/", include("timeclock.urls")),
    path("msgraph/", include("ms_tasks.urls")),

    # --- Admin/Auth/Start ---
    path("", RedirectView.as_view(pattern_name="crm_core:dashboard", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
]

# ---- Aliase für ältere/abweichende Pfade ----
# 1) E-Mail statt "mail" in der URL (Button "Vormerken" ruft oft /crm/email/.../to-expense/ auf)
urlpatterns += [
    path("crm/email/<str:message_id>/to-expense/", vmail.mail_to_expense, name="mail_to_expense_email"),
    path("crm/email/<str:message_id>/to-task/",    vmail.mail_to_task,    name="mail_to_task_email"),
]

# 2) Ohne trailing slash bei add
urlpatterns += [
    path("crm/expenses/drafts/add", expenses_views.draft_add, name="expenses_draft_add_noslash"),
]
# --- OCR alias routes (GET erlaubt, Slash + No-Slash) ---

try:
    urlpatterns
except NameError:
    urlpatterns = []
    path("crm/inbox/attachment/save", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    path("crm/inbox/attachment/save-invoice", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/save-invoice/?$", ocr_views.attachments_save_invoice, name="attachments_save_invoice_catchall"),
    # --- BEGIN CRM EXPORT ROUTES ---
    path("crm/expenses/drafts/export.xlsx", exp_views.drafts_export_xlsx, name="drafts_export"),
    path("crm/expenses/drafts/export", exp_views.drafts_export_xlsx),
    path("crm/expenses/export.xlsx", exp_views.drafts_export_xlsx),
    path("crm/expenses/export", exp_views.drafts_export_xlsx),
    # --- END CRM EXPORT ROUTES ---
        # Export der Ausgaben-Entwürfe (mehrere Schreibweisen kompatibel)
    path("crm/expenses/draft/edit/", safe_views.draft_edit_fallback2),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/expenses/ocr/from-email/", exp_views.ocr_from_email, name="ocr_from_email"),
    path("crm/invoices/draft/from-email/", invoices_draft_from_email, name="invoices_draft_from_email"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/inbox/attachment/ocr", attachments_ocr_get, name="attachment_ocr"),
    path("crm/inbox/attachment/ocr/", attachments_ocr_get),

urlpatterns += [
]
from django.views.generic.base import RedirectView

try:
    urlpatterns
except NameError:
    urlpatterns = []
    path("crm/inbox/attachment/save", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    path("crm/inbox/attachment/save-invoice", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/save-invoice/?$", ocr_views.attachments_save_invoice, name="attachments_save_invoice_catchall"),
    # --- BEGIN CRM EXPORT ROUTES ---
    path("crm/expenses/drafts/export.xlsx", exp_views.drafts_export_xlsx, name="drafts_export"),
    path("crm/expenses/drafts/export", exp_views.drafts_export_xlsx),
    path("crm/expenses/export.xlsx", exp_views.drafts_export_xlsx),
    path("crm/expenses/export", exp_views.drafts_export_xlsx),
    # --- END CRM EXPORT ROUTES ---
        # Export der Ausgaben-Entwürfe (mehrere Schreibweisen kompatibel)
    path("crm/expenses/draft/edit/", safe_views.draft_edit_fallback2),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/expenses/ocr/from-email/", exp_views.ocr_from_email, name="ocr_from_email"),
    path("crm/invoices/draft/from-email/", invoices_draft_from_email, name="invoices_draft_from_email"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/inbox/attachment/ocr", attachments_ocr_get, name="attachment_ocr"),
    path("crm/inbox/attachment/ocr/", attachments_ocr_get),

urlpatterns += [
]
from django.views.generic.base import RedirectView

try:
    urlpatterns
except NameError:
    urlpatterns = []
    path("crm/inbox/attachment/save", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    path("crm/inbox/attachment/save-invoice", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/save-invoice/?$", ocr_views.attachments_save_invoice, name="attachments_save_invoice_catchall"),
    # --- BEGIN CRM EXPORT ROUTES ---
    path("crm/expenses/drafts/export.xlsx", exp_views.drafts_export_xlsx, name="drafts_export"),
    path("crm/expenses/drafts/export", exp_views.drafts_export_xlsx),
    path("crm/expenses/export.xlsx", exp_views.drafts_export_xlsx),
    path("crm/expenses/export", exp_views.drafts_export_xlsx),
    # --- END CRM EXPORT ROUTES ---
        # Export der Ausgaben-Entwürfe (mehrere Schreibweisen kompatibel)
    path("crm/expenses/draft/edit/", safe_views.draft_edit_fallback2),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/expenses/ocr/from-email/", exp_views.ocr_from_email, name="ocr_from_email"),
    path("crm/invoices/draft/from-email/", invoices_draft_from_email, name="invoices_draft_from_email"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/inbox/attachment/ocr", attachments_ocr_get, name="attachment_ocr"),
    path("crm/inbox/attachment/ocr/", attachments_ocr_get),

urlpatterns += [
]

# ==== OCR routes (clean) ====
from django.shortcuts import redirect
from django.urls import path, re_path, re_path

def attachments_ocr_get(request, *args, **kwargs):
    p = request.GET.copy()
    msg = p.get("mid") or p.get("message_id") or p.get("messageId") or p.get("id")
    att = p.get("aid") or p.get("attachment_id") or p.get("attachmentId")
    if msg:
        p["mid"] = msg
    if att:
        p["aid"] = att
    p["ocr"]="1"
    p["pick"]="1"
    return redirect("/crm/invoices/draft/from-email/?" + p.urlencode())

try:
    urlpatterns
except NameError:
    urlpatterns = []
    path("crm/inbox/attachment/save", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    path("crm/inbox/attachment/save-invoice", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/save-invoice/?$", ocr_views.attachments_save_invoice, name="attachments_save_invoice_catchall"),
    # --- BEGIN CRM EXPORT ROUTES ---
    path("crm/expenses/drafts/export.xlsx", exp_views.drafts_export_xlsx, name="drafts_export"),
    path("crm/expenses/drafts/export", exp_views.drafts_export_xlsx),
    path("crm/expenses/export.xlsx", exp_views.drafts_export_xlsx),
    path("crm/expenses/export", exp_views.drafts_export_xlsx),
    # --- END CRM EXPORT ROUTES ---
        # Export der Ausgaben-Entwürfe (mehrere Schreibweisen kompatibel)
    path("crm/expenses/draft/edit/", safe_views.draft_edit_fallback2),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/expenses/ocr/from-email/", exp_views.ocr_from_email, name="ocr_from_email"),
    path("crm/invoices/draft/from-email/", invoices_draft_from_email, name="invoices_draft_from_email"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/inbox/attachment/ocr", attachments_ocr_get, name="attachment_ocr"),
    path("crm/inbox/attachment/ocr/", attachments_ocr_get),

urlpatterns += [
]
# ==== /OCR routes ====

# ==== OCR routes (clean, unique) ====
from django.shortcuts import redirect
from django.urls import path, re_path, re_path

def attachments_ocr_get(request, *args, **kwargs):
    p = request.GET.copy()
    msg = p.get("mid") or p.get("message_id") or p.get("messageId") or p.get("id")
    att = p.get("aid") or p.get("attachment_id") or p.get("attachmentId")
    if msg:
        p["mid"] = msg
    if att:
        p["aid"] = att
    p["ocr"] = "1"
    return redirect("/crm/invoices/draft/from-email/?" + p.urlencode())

try:
    urlpatterns
except NameError:
    urlpatterns = []
    path("crm/inbox/attachment/save", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    path("crm/inbox/attachment/save-invoice", ocr_views.attachments_save_invoice, name="attachment_save_invoice"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/save-invoice/?$", ocr_views.attachments_save_invoice, name="attachments_save_invoice_catchall"),
    # --- BEGIN CRM EXPORT ROUTES ---
    path("crm/expenses/drafts/export.xlsx", exp_views.drafts_export_xlsx, name="drafts_export"),
    path("crm/expenses/drafts/export", exp_views.drafts_export_xlsx),
    path("crm/expenses/export.xlsx", exp_views.drafts_export_xlsx),
    path("crm/expenses/export", exp_views.drafts_export_xlsx),
    # --- END CRM EXPORT ROUTES ---
        # Export der Ausgaben-Entwürfe (mehrere Schreibweisen kompatibel)
    path("crm/expenses/draft/edit/", safe_views.draft_edit_fallback2),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/expenses/ocr/from-email/", exp_views.ocr_from_email, name="ocr_from_email"),
    path("crm/invoices/draft/from-email/", invoices_draft_from_email, name="invoices_draft_from_email"),
    re_path(r"^crm/inbox/.+/(attachment|attachments)/ocr/?$", attachments_ocr_get, name="attachments_ocr_catchall"),
    path("crm/inbox/attachment/ocr", attachments_ocr_get, name="attachment_ocr"),
    path("crm/inbox/attachment/ocr/", attachments_ocr_get),

urlpatterns += [
    path("crm/inbox/attachments/ocr", attachments_ocr_get, name="attachments_ocr"),
    path("crm/inbox/attachments/ocr/", attachments_ocr_get),
]
# ==== /OCR routes ====

# --- injected: expenses delete route ---
try:
    urlpatterns += [
        path("crm/expenses/drafts/delete/", exp_views.draft_delete, name="draft_delete"),
    ]
except NameError:
    from django.urls import path
    urlpatterns = globals().get("urlpatterns", [])
    urlpatterns += [
        path("crm/expenses/drafts/delete/", exp_views.draft_delete, name="draft_delete"),
    ]
# --- end injected ---
handler500 = "crm_core.views_safe.error5002"
