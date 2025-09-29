from django.urls import path, include
from . import views_download
from . import views

app_name = "crm_core"

urlpatterns = [
    path("files/download/", views_download.download_file, name="files_download"),
    path("files/view/", views_download.view_file, name="files_view"),
    path("email/<str:message_id>/save-contact/", views.email_contact_quickadd, name="email_contact_quickadd"),
    path("email/<str:message_id>/attachments/<str:attachment_id>/save/", views.email_attachment_save, name="email_attachment_save"),
    path("", views.dashboard, name="dashboard"),
    path("email/<str:message_id>/reply/", views.email_reply, name="email_reply"),
    path("email/<str:message_id>/reply-all/", views.email_reply_all, name="email_reply_all"),
    path("email/<str:message_id>/forward/", views.email_forward, name="email_forward"),
    path("email/<str:message_id>/reply/", views.email_reply, name="email_reply"),
    path("email/<str:message_id>/reply-all/", views.email_reply_all, name="email_reply_all"),
    path("email/<str:message_id>/forward/", views.email_forward, name="email_forward"),

    # Dashboard
    path("", views.dashboard, name="home"),

    # Microsoft Login (alte, gängige Namen)
    path("auth/microsoft/", views.microsoft_auth_init, name="microsoft_auth_init"),
    path("auth/microsoft/callback/", views.microsoft_auth_callback, name="microsoft_auth_callback"),

    # Firmen
    path("companies/", views.company_list, name="company_list"),
    path("companies/create/", views.company_create, name="company_create"),
    path("companies/<int:pk>/", views.company_detail, name="company_detail"),
    path("companies/<int:pk>/edit/", views.company_update, name="company_update"),
    path("companies/<int:pk>/delete/", views.company_delete, name="company_delete"),
    path("contacts/<int:pk>/delete/",  views.contact_delete, name="contact_delete"),


    # Kontakte
    path("contacts/", views.contact_list, name="contact_list"),
    path("contacts/create/", views.contact_create, name="contact_create"),
    path("contacts/<int:pk>/", views.contact_detail, name="contact_detail"),
    path("contacts/<int:pk>/edit/", views.contact_update, name="contact_update"),
    path("contacts/<path:filename>/delete/", views.contact_delete, name="contact_delete"),


    # Mail
    path("email/", views.email_home, name="email_home"),
    path("inbox/", views.inbox_view, name="inbox"),
    path("sent/", views.sent_view, name="sent"),
    path("email/refresh/", views.email_refresh, name="email_refresh"),
    path("email/inbox/", views.email_inbox, name="email_inbox"),
    path("email/compose/", views.email_compose, name="email_compose"),
    # path("email/send/", views.email_send, name="email_send"),
    path("email/<str:message_id>/", views.email_detail, name="email_detail"),
    path("email/<str:message_id>/attachments/", views.email_attachments, name="email_attachments"),
    path("email/<str:message_id>/attachments/<str:attachment_id>/download/",
         views.email_attachment_download, name="email_attachment_download"),
    path("email/create_contact/", views.contact_create_from_email, name="contact_create_from_email"),
    path("email/logs/", views.email_log_list, name="email_log_list"),

    # Dateien
    path("files/", views.files_list, name="files_list"),
    path("files/list/", views.files_list, name="files_list_alias"),
    path("files/upload/", views.files_upload, name="files_upload"),
    path("files/<path:filename>/download/", views.files_download, name="files_download"),
    path("files/<path:filename>/delete/", views.files_delete, name="files_delete"),
    

    # Kalender
    path("calendar/list/", views.calendar_list, name="calendar_list"),
    path("calendar/create/", views.calendar_create, name="calendar_create"),
    path("calendar/<str:event_id>/", views.calendar_detail, name="calendar_detail"),
    path("calendar/<str:event_id>/edit/", views.calendar_edit, name="calendar_edit"),
    path("calendar/<str:event_id>/delete/", views.calendar_delete, name="calendar_delete"),


    # VOIP
    path("voip/call/", views.call_number_via_sipgate, name="call_number_via_sipgate"),
    path("voip/calls/", views.fritzbox_call_list, name="fritzbox_call_list"),
    path("voip/fritz/calllist/", views.fritzbox_call_list, name="fritzbox_call_list"),

    # TASKS
    path("msgraph/", include("ms_tasks.urls")),    
]

