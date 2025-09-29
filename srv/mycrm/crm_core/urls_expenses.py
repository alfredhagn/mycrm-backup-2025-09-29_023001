from django.urls import path
from . import views_expenses as V

# Minimal & robust: nur die Mailimport-Route über die Bridge, sonst nichts kaputtmachen.
urlpatterns = [
    path('expenses/draft/from-email/', V.draft_from_email_bridge, name='exp_draft_from_email'),
    path('expenses/drafts/delete/<int:idx>/', V.draft_delete, name='exp_draft_delete_idx'),
    path('expenses/drafts/edit/<int:idx>/', V.draft_edit, name='exp_draft_edit_idx'),
    path('expenses/drafts/delete/', V.draft_delete, name='exp_draft_delete'),
    path('expenses/drafts/update/', V.draft_update, name='exp_draft_update'),
    path('expenses/drafts/edit/', V.draft_edit, name='exp_draft_edit'),
    path('expenses/ocr/from-email/', V.ocr_from_email, name='exp_ocr_from_email'),

]
