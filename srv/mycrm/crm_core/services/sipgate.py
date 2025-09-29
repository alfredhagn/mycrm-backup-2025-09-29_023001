# crm_core/services/sipgate.py
import os
import re
import requests
from django.conf import settings

API_BASE = getattr(settings, "SIPGATE_API_BASE", "https://api.sipgate.com")

def _env(key, default=None):
    return getattr(settings, key, None) or os.getenv(key, default)

def _normalize_number(number: str) -> str:
    """Very small E.164-normalizer with DE default. Adjust to your needs."""
    if not number:
        return number
    s = re.sub(r"[^0-9+]+", "", number)
    if s.startswith("+"):
        return s
    if s.startswith("00"):
        return "+" + s[2:]
    cc = _env("DEFAULT_COUNTRY_CODE", "DE").upper()
    country_map = {"DE": "+49", "AT": "+43", "CH": "+41"}
    prefix = country_map.get(cc, "+49")
    if s.startswith("0"):  # national
        return prefix + s[1:]
    # already international without '+' (rare)
    return "+" + s

def click_to_call(destination_number: str) -> None:
    token_id = _env("SIPGATE_TOKEN_ID")
    token    = _env("SIPGATE_TOKEN")
    device_id= _env("SIPGATE_DEVICE_ID")
    caller   = _env("SIPGATE_CALLER")  # your outgoing caller ID (E.164 or internal)
    if not all([token_id, token, device_id, caller]):
        raise RuntimeError("SIPGATE_* env/settings fehlen (TOKEN_ID, TOKEN, DEVICE_ID, CALLER)." )

    callee = _normalize_number(destination_number)
    url = f"{API_BASE}/v2/sessions/calls"
    payload = {
        "deviceId": device_id,
        "caller": caller,
        "callee": callee,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Sipgate-Client": "mycrm/1.0",
    }
    resp = requests.post(url, json=payload, auth=(token_id, token), headers=headers, timeout=15)
    if resp.status_code not in (200, 201, 202):
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise RuntimeError(f"Sipgate API Fehler {resp.status_code}: {detail}")