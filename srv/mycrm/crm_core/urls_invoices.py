from django.urls import path
from . import views as V

urlpatterns = [
    path('invoices/draft/from-email/', V.draft_from_email_bridge, name='inv_draft_from_email'),
]
