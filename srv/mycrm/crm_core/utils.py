# crm_core/utils.py
import re
def normalize_phone(num: str) -> str:
    if not num: return ""
    s = re.sub(r"\D+","", num)
    if s.startswith("00"): s = s[2:]
    if s.startswith("0"):  s = "49" + s[1:]   # DE-Default, bei dir ggf. +43/+49 kombinieren
    return "+" + s

