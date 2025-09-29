def list_attachments(sess, message_id):
    url = f"https://graph.microsoft.com/v1.0/me/messages/{message_id}/attachments?$top=50"
    r = sess.get(url, timeout=20); r.raise_for_status()
    data = r.json()
    items = data.get("value", [])
    return [a for a in items if a.get("@odata.type") == "#microsoft.graph.fileAttachment"]

def fetch_attachment_bytes(sess, message_id, attachment_id):
    from urllib.parse import quote
    url = f"https://graph.microsoft.com/v1.0/me/messages/{quote(message_id, safe="")}/attachments/{quote(attachment_id, safe="")}/$value"
    r = sess.get(url, timeout=30); r.raise_for_status()
    return r.content
