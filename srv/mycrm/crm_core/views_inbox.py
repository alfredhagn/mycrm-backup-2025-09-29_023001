# --- OCR-Redirect (übernimmt Query + setzt ocr=1) ---
from urllib.parse import urlencode
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def attachments_ocr_redirect(request):
    params = request.GET.copy()
    params["ocr"] = "1"
    return redirect(f"/crm/inbox/attachments/save/?{urlencode(params, doseq=True)}")
