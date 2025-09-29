# views.py – korrigiert am 18.08.2025 (Basis: mycrm_current_20250817.tar.gz)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

from crm_core.models import Contact, Company, EmailLog
from timeclock.models import TimeEntry


@login_required
def dashboard(request):
    return render(request, "crm_core/dashboard.html")


@login_required
def email_list(request):
    emails = EmailLog.objects.all().order_by("-timestamp")
    return render(request, "crm_core/email_list.html", {"messages": emails})


@login_required
def email_detail(request, message_id):
    message = get_object_or_404(EmailLog, id=message_id)

    if request.method == "POST" and request.POST.get("create_contact") == "1":
        # Kontakt aus der E-Mail erzeugen → nur wenn Button ausgelöst wird
        Contact.objects.create(
            first_name="",
            last_name="",
            email=message.recipient
        )
        messages.success(request, "Kontakt erfolgreich angelegt.")
        return HttpResponseRedirect(
            reverse("crm:email_detail", args=[message_id])
        )

    return render(
        request,
        "crm_core/email_detail.html",
        {"message": message, "message_id": message_id},
    )


@login_required
def email_reply(request, message_id):
    """
    Einfacher Reply-Stub (funktional, aber ohne Versand).
    """
    message = get_object_or_404(EmailLog, id=message_id)
    if request.method == "POST":
        messages.info(request, "Antwort wurde (noch) nicht versendet – Funktion nicht implementiert.")
        return HttpResponseRedirect(reverse("crm:email_detail", args=[message_id]))

    return render(
        request,
        "crm_core/email_reply.html",
        {"message": message}
    )


@login_required
def calendar_list(request):
    entries = TimeEntry.objects.all().order_by("-start_time")
    return render(request, "crm_core/calendar_list.html", {"entries": entries})


@login_required
def contacts_list(request):
    contacts = Contact.objects.all().order_by("last_name")
    return render(request, "crm_core/contacts_list.html", {"contacts": contacts})


@login_required
def companies_list(request):
    companies = Company.objects.all().order_by("name")
    return render(request, "crm_core/companies_list.html", {"companies": companies})


@login_required
def files_list(request):
    return render(request, "crm_core/files_list.html")


@login_required
def voip_fritz_calllist(request):
    return render(request, "crm_core/voip_fritz_calllist.html")


@login_required
def calendar_day_view(request):
    return render(request, "crm_core/calendar_day.html")


@login_required
def calendar_week_view(request):
    return render(request, "crm_core/calendar_week.html")


@login_required
def calendar_month_view(request):
    return render(request, "crm_core/calendar_month.html")


# ---- (weiter mit TimeEntry- und Search-Views in Block 2/2) ----
@login_required
def time_entries_list(request):
    entries = TimeEntry.objects.all().order_by("-start_time")
    return render(request, "crm_core/time_entries_list.html", {"entries": entries})


@login_required
def time_entry_detail(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id)
    return render(request, "crm_core/time_entry_detail.html", {"entry": entry})


@login_required
def time_entry_add(request):
    if request.method == "POST":
        # TODO: Form processing (original code omitted here)
        return redirect(reverse("crm:time_entries"))
    return render(request, "crm_core/time_entry_form.html")


@login_required
def time_entry_edit(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id)
    if request.method == "POST":
        # TODO: update logic (original code omitted here)
        return redirect(reverse("crm:time_entries"))
    return render(request, "crm_core/time_entry_form.html", {"entry": entry})


@login_required
def search(request):
    query = request.GET.get("q", "")
    contacts = Contact.objects.filter(last_name__icontains=query)
    companies = Company.objects.filter(name__icontains=query)
    return render(
        request,
        "crm_core/search_results.html",
        {"contacts": contacts, "companies": companies, "query": query},
    )


@login_required
def not_implemented(request):
    messages.warning(request, "Diese Funktion ist noch nicht implementiert.")
    return redirect(reverse("crm:dashboard"))


# End of file (Basisversion ohne weiteren Patch)
