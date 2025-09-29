# -*- coding: utf-8 -*-
import requests, urllib.parse
from datetime import datetime

def _graph_token_for(user):
    try:
        from allauth.socialaccount.models import SocialToken
        tok = (SocialToken.objects
               .filter(account__user=user, app__provider="microsoft")
               .order_by("-id").first())
        return tok.token if tok else None
    except Exception:
        return None

def _hdr(token:str) -> dict:
    return {"Authorization": f"Bearer {token}"}

def od_get_item_by_path(token:str, path:str):
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(path.strip('/'), safe='/')}"
    r = requests.get(url, headers=_hdr(token), timeout=20)
    return r if r.status_code == 200 else None

def od_create_folder(token:str, parent_path:str, name:str):
    name = name.strip("/")
    if not parent_path:
        url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
    else:
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(parent_path.strip('/'), safe='/')}:/children"
    payload = {"name": name, "folder": {}, "@microsoft.graph.conflictBehavior": "replace"}
    r = requests.post(url, json=payload, headers=_hdr(token), timeout=20)
    if r.status_code in (200,201):
        return r.json()
    # Falls existiert o. ä., ignorieren – zuvor wurde GET probiert
    return None

def od_ensure_folder(user, full_path:str):
    """legt /MyCRM/Belege/JJJJ/MM etc. an (segmentweise)"""
    token = _graph_token_for(user)
    if not token:
        return None
    full_path = full_path.strip("/")
    if not full_path:
        return {"webUrl": None, "id": "root"}
    segs = full_path.split("/")
    curr = ""
    for s in segs:
        curr = f"{curr}/{s}" if curr else s
        # existiert?
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(curr, safe='/')}"
        r = requests.get(url, headers=_hdr(token), timeout=20)
        if r.status_code == 404:
            parent = "/".join(curr.split("/")[:-1])
            od_create_folder(token, parent, s)
    # Return letztes Item
    r = requests.get(f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(curr, safe='/')}",
                     headers=_hdr(token), timeout=20)
    return r.json() if r.status_code == 200 else None

def od_upload_bytes(user, folder_path:str, filename:str, data:bytes):
    """PUT /content → legt die Datei ab, gibt DriveItem (inkl. webUrl) zurück"""
    token = _graph_token_for(user)
    if not token:
        return None
    if not data:
        data = b""
    if folder_path:
        od_ensure_folder(user, folder_path)
        graph_path = f"{folder_path.strip('/')}/{filename}"
    else:
        graph_path = filename
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{urllib.parse.quote(graph_path, safe='/')}:/content"
    r = requests.put(url, headers=_hdr(token), data=data, timeout=60)
    if r.status_code in (200,201):
        return r.json()
    return None
