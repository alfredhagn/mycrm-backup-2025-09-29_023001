from datetime import timedelta
from django.utils import timezone

# Platzhalter: ersetze diese Funktionen bei Bedarf mit deiner echten Graph-Client-Logik
def get_message(user, message_id):
    # TODO: MS Graph: GET /me/messages/{id}
    return {"id": message_id, "subject": f"Mail {message_id}", "from": {"emailAddress": {"address":"noreply@example.com"}}, "hasAttachments": False}

def iter_attachments(user, message_id):
    # TODO: MS Graph: /me/messages/{id}/attachments
    yield from ()

def save_attachment_to_folder(att, abs_folder):
    # TODO: Datei-Inhalt schreiben; hier nur Platzhalter-Name
    return (abs_folder, att.get('name') or 'anhang.bin')

def teams_create_online_meeting(user, title, start, end):
    # TODO: POST /me/onlineMeetings
    return {"joinWebUrl": "https://teams.microsoft.com/l/meetup-join/PLACEHOLDER"}

def sharepoint_ensure_folder(user, company_name):
    # TODO: Graph/SharePoint-API, Ordner-Pfad nach Schema implementieren
    # Rückgabe: (webUrl, driveItemId)
    safe = company_name.replace('/', '_')
    return (f"https://sharepoint.example.com/sites/CRM/Shared%20Documents/Firmen/{safe}", f"driveItem-{safe}")

def guess_supplier_from_email(addr):
    if not addr: return ""
    dom = addr.split("@")[-1]
    return dom.split(".")[0].title()

def parse_amount_from_subject(subject):
    # sehr einfache Heuristik: erstes €-Vorkommen
    import re
    m = re.search(r'(\d+[.,]\d{2})\s*€|€\s*(\d+[.,]\d{2})', subject or "")
    if not m: return None
    val = m.group(1) or m.group(2)
    return float(val.replace('.', '').replace(',', '.'))
